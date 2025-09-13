from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
from speech_to_sign import recognize_speech, play_videos_for_sentence, proses_teks  # Ganti dengan nama yang benar dari program

app = Flask(__name__)
CORS(app)

# Status global untuk menentukan apakah program sedang berjalan
is_running = False

# Menjalankan proses speech-to-text di thread terpisah
def run_speech_recognition():
    recognize_speech()

# API untuk memulai proses
@app.route('/start', methods=['POST'])
def start():
    global is_running
    if not is_running:
        is_running = True
        # Mulai thread untuk mengenali suara
        speech_thread = threading.Thread(target=run_speech_recognition)
        speech_thread.daemon = True
        speech_thread.start()
        return jsonify({"status": "started", "message": "Speech recognition started"}), 200
    else:
        return jsonify({"status": "error", "message": "Already running"}), 400

# API untuk menghentikan proses
@app.route('/stop', methods=['POST'])
def stop():
    global is_running
    if is_running:
        is_running = False
        # TODO: Stop the speech recognition process
        return jsonify({"status": "stopped", "message": "Speech recognition stopped"}), 200
    else:
        return jsonify({"status": "error", "message": "Not running"}), 400

# API untuk mengirimkan hasil video bahasa isyarat dan teks
@app.route('/get_results', methods=['GET'])
def get_results():
    if is_running:
        # Kirim hasil video dan teks yang telah diproses
        result_text = proses_teks()  # Gantikan dengan cara mengakses hasil yang telah diproses
        result_video = play_videos_for_sentence()
        return jsonify(result_text, result_video), 200
    else:
        return jsonify({"status": "error", "message": "Not running"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
