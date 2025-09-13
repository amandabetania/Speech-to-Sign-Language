import os
import cv2
import time
import pygame
import threading
import requests
import speech_recognition as sr
from queue import Queue

# Daftar imbuhan yang tersedia dalam kamus bahasa isyarat
imbuhan = ['ter', 'ber', 'me', 'di', 'se', 'ke', 'nya', "kan", "an", "lah", "kah", "pun"]

# Direktori tempat menyimpan video bahasa isyarat
kamus_bahasa_isyarat_dir = r'D:\\Documents\\DeafFriends\\backend\\sign_video'

# Queue untuk menyimpan kalimat yang terdeteksi
sentence_queue = Queue()

# Variabel global untuk teks
text_list = []  # Teks yang terdeteksi dan diproses

# Fungsi untuk menangkap suara dan memproses teks secara real-time
def recognize_speech():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Mendengarkan...")
        recognizer.adjust_for_ambient_noise(source)

        current_sentence = ""  # Kalimat yang sedang dibentuk
        last_time = time.time()  # Waktu saat suara terakhir diterima

        while True:
            try:
                audio = recognizer.listen(source, timeout=10)

                text = recognizer.recognize_google(audio, language='id-ID')
                print(f"Deteksi Teks: {text}")

                current_sentence += " " + text  # Menambahkan teks ke kalimat yang sedang berlangsung

                # Jika ada jeda lebih dari 1 detik, anggap ini sebagai kalimat baru
                if time.time() - last_time > 1:
                    if current_sentence.strip():
                        processed_text = proses_teks(current_sentence.strip())
                        print(f"Kalimat Baru: {current_sentence.strip()}")

                        # # Kirim teks ke Flask API untuk mendapatkan video
                        # response = requests.post('http://localhost:5000/get_sign_language_video', json={'text': processed_text})
                        # if response.status_code == 200:
                        #     video_files = response.json().get('videos', [])
                        #     print(f"Video untuk kalimat: {video_files}")

                    current_sentence = ""  # Reset kalimat yang sedang berlangsung
                last_time = time.time()

            except sr.WaitTimeoutError:
                print("Tidak ada suara yang terdeteksi. Mencoba lagi...")
                continue
            except sr.RequestError:
                print("Permintaan gagal. Cek koneksi internet.")
                break
            except sr.UnknownValueError:
                print("Gagal mengenali ucapan.")
                continue


# Fungsi untuk memeriksa dan memisahkan imbuhan
def proses_imbuhan(kata):
    for imbu in imbuhan:
        if kata.startswith(imbu):  # Jika kata diawali dengan imbuhan
            root_kata = kata[len(imbu):]  # Ambil kata setelah imbuhan
            return imbu, root_kata
        elif kata.endswith(imbu):  # Jika imbuhan ada di akhir kata
            root_kata = kata[:-len(imbu)]  # Ambil kata sebelum imbuhan
            return imbu, root_kata
    return None, kata  # Jika tidak ada imbuhan, kembalikan kata utuh

# Fungsi untuk memproses teks yang dihasilkan dari speech-to-text
def proses_teks(teks):
    print(f"Teks sebelum preprocessing: {teks}")  # Menampilkan teks asli
    
    kalimat = teks.split()  # Pisahkan teks menjadi kata-kata
    hasil_kalimat = []

    for kata in kalimat:
        imbuhan_ditemukan, kata_utama = proses_imbuhan(kata)
        
        print(f"Memproses kata: {kata} -> Kata utama: {kata_utama}")  # Menampilkan kata yang sedang diproses

        # Pisahkan imbuhan dan kata utama dengan spasi
        if imbuhan_ditemukan:
            hasil_kalimat.append(imbuhan_ditemukan + ' ' + kata_utama)
        else:
            hasil_kalimat.append(kata_utama)

    hasil_akhir = ' '.join(hasil_kalimat)
    print(f"Teks setelah preprocessing: {hasil_akhir}")  # Menampilkan teks setelah diproses
    return hasil_akhir  # Mengembalikan teks yang telah diproses

# Fungsi untuk mencocokkan teks dengan video
def match_text_to_video(cleaned_text):
    words = cleaned_text.split()
    video_files = []

    for word in words:
        word_capitalized = word.capitalize()

        # Check if the video exists in the sign_video folder
        video_path = os.path.join(kamus_bahasa_isyarat_dir, f"{word_capitalized}.webm")
        if os.path.exists(video_path):  # Check if the video file exists
            video_files.append(video_path)
        else:
            print(f"Tidak ada video untuk kata: {word_capitalized}")
            # If no video for the word, break it down to letters
            video_found = False  # Flag to track if any letter video is found
            for letter in word:
                letter_capitalized = letter.upper()  # Capitalize the letter
                video_letter_path = os.path.join(kamus_bahasa_isyarat_dir, f"{letter_capitalized}.webm")
                if os.path.exists(video_letter_path):  # Check if there's a video for the letter
                    video_files.append(video_letter_path)
                    video_found = True
                else:
                    print(f"Tidak ada video untuk huruf: {letter_capitalized}")
            
            # If no video was found for the word or its letters, return and stop searching
            if not video_found:
                print(f"Tidak ada video untuk kata atau huruf: {word}")
                return []  # Return empty list to indicate no videos were found

    # Debug: Print the videos found for the text
    print(f"Video untuk teks '{cleaned_text}': {video_files}")
    
    return video_files

# Fungsi untuk memutar daftar video
def play_videos_for_sentence(sentence, speed_factor=5.0):
    video_files = match_text_to_video(sentence)  # Mencocokkan teks dengan video

    if video_files:
        for video_path in video_files:
            print(f"Memutar video: {video_path}")
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                print(f"Gagal membuka video: {video_path}")
                continue

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow("Bahasa Isyarat", frame)

                # Menghitung kecepatan pemutaran video berdasarkan faktor kecepatan
                frame_delay = int(30 / speed_factor)  # Kecepatan berdasarkan faktor yang diberikan
                key = cv2.waitKey(frame_delay)

                if key == ord('q') or cv2.getWindowProperty("Bahasa Isyarat", cv2.WND_PROP_VISIBLE) < 1:
                    print("Jendela ditutup. Program dihentikan.")
                    cap.release()
                    cv2.destroyAllWindows()
                    return  # Keluar dari fungsi jika jendela ditutup
            cap.release()

# Fungsi untuk menjalankan pengenalan suara dalam thread terpisah
def start_speech_recognition():
    speech_thread = threading.Thread(target=recognize_speech)
    speech_thread.daemon = True  # Agar thread berhenti saat program utama berhenti
    speech_thread.start()

# Memulai pengenalan suara
start_speech_recognition()

