import threading
import time
import cv2
import os
from queue import Queue
from flask import Flask, jsonify, request
from flask_cors import CORS
from speech_to_sign import proses_teks, recognize_speech

app = Flask(__name__)
CORS(app)

# Inisialisasi queue dan status
sentence_queue = Queue()
program_running = False
is_speech_recognized = False

kamus_bahasa_isyarat_dir = r'D:\sensebridge\backend\sign_video' 

def match_text_to_video(cleaned_text):
    words = cleaned_text.split()
    video_files = []

    for word in words:
        word_capitalized = word.capitalize()
        video_path = os.path.join(kamus_bahasa_isyarat_dir, f"{word_capitalized}.webm")
        if os.path.exists(video_path):
            video_files.append(video_path)
        else:
            print(f"Tidak ada video untuk kata: {word_capitalized}")
            video_found = False
            for letter in word:
                letter_capitalized = letter.upper()
                video_letter_path = os.path.join(kamus_bahasa_isyarat_dir, f"{letter_capitalized}.webm")
                if os.path.exists(video_letter_path):
                    video_files.append(video_letter_path)
                    video_found = True
                else:
                    print(f"Tidak ada video untuk huruf: {letter_capitalized}")
            if not video_found:
                print(f"Tidak ada video untuk kata atau huruf: {word}")
                return []
    return video_files

def process_queue():
    global is_speech_recognized
    while program_running:
        if not sentence_queue.empty():
            current_sentence = sentence_queue.get()
            video_files = match_text_to_video(current_sentence)
            print(f"Video yang ditemukan untuk '{current_sentence}': {video_files}")
            is_speech_recognized = True  # Set status jika kalimat dikenali
        time.sleep(1)

@app.route('/start', methods=['POST'])
def start():
    global program_running, is_speech_recognized
    if not program_running:
        program_running = True
        is_speech_recognized = False
        speech_thread = threading.Thread(target=recognize_speech)
        queue_thread = threading.Thread(target=process_queue)
        speech_thread.daemon = True
        queue_thread.daemon = True
        speech_thread.start()
        queue_thread.start()
        return jsonify({"status": "Program dimulai"})
    else:
        return jsonify({"status": "Program sudah berjalan"})

@app.route('/stop', methods=['POST'])
def stop():
    global program_running
    program_running = False
    return jsonify({"status": "Program dihentikan"})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "program_running": program_running,
        "speech_recognized": is_speech_recognized,
        "current_text": sentence_queue.queue[-1] if not sentence_queue.empty() else ""
    })

@app.route('/process_text', methods=['POST'])
def process_text():
    input_text = request.json.get("text")
    
    # Proses teks untuk preprocessing
    cleaned_text = proses_teks(input_text)  # Fungsi yang digunakan untuk memproses teks
    
    # Menambahkan teks yang sudah diproses ke antrian
    sentence_queue.put(cleaned_text)
    
    print(f"Kalimat setelah preprocessing: {cleaned_text}")
    
    return jsonify({"status": "Teks diproses dan ditambahkan ke antrian", "processed_text": cleaned_text})

@app.route('/get_sign_language_video', methods=['GET'])
def get_sign_language_video():
    if not sentence_queue.empty():
        current_sentence = sentence_queue.queue[0]  # Ambil kalimat teratas tanpa mengeluarkannya
        video_files = match_text_to_video(current_sentence)

        if video_files:
            print(f"Video ditemukan untuk kalimat '{current_sentence}': {video_files}")
            return jsonify({"videos": video_files})
        else:
            print(f"Tidak ada video ditemukan untuk kalimat '{current_sentence}'")
            return jsonify({"videos": [], "message": "Tidak ada video yang ditemukan untuk teks yang diberikan."})
    else:
        print("Antrian kalimat kosong.")
        return jsonify({"videos": [], "message": "Antrian kalimat kosong."})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)