import speech_recognition as sr
import time

# Fungsi untuk menangkap suara secara terus-menerus
def recognize_speech():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Variabel global untuk teks
    text_list = []

    # Menunggu input suara
    with microphone as source:
        print("Mendengarkan...")
        recognizer.adjust_for_ambient_noise(source)  # Menyesuaikan dengan noise sekitar

        current_sentence = ""  # Kalimat yang sedang dibentuk
        last_time = time.time()  # Waktu saat suara terakhir diterima

        while True:
            try:
                # Mendengarkan suara
                audio = recognizer.listen(source, timeout=10)

                # Mengonversi suara menjadi teks
                text = recognizer.recognize_google(audio, language='id-ID')
                print(f"Deteksi Teks: {text}")

                current_sentence += " " + text  # Menambahkan teks ke kalimat yang sedang berlangsung

                # Jika ada jeda lebih dari 1 detik, anggap ini sebagai kalimat baru
                if time.time() - last_time > 1:  # Jika lebih dari 1 detik tanpa suara
                    if current_sentence.strip():  # Cek apakah kalimat tidak kosong
                        text_list.append(current_sentence.strip())  # Menyimpan kalimat baru
                        print(f"Kalimat Baru: {current_sentence.strip()}")
                    current_sentence = ""  # Reset kalimat yang sedang berlangsung

                last_time = time.time()  # Update waktu terakhir deteksi

            except sr.WaitTimeoutError:
                print("Tidak ada suara yang terdeteksi. Mencoba lagi...")
                continue
            except sr.RequestError:
                print("Permintaan gagal. Cek koneksi internet.")
                break
            except sr.UnknownValueError:
                print("Gagal mengenali ucapan.")
                continue
    
    # Mengembalikan list teks hasil pengenalan suara
    return text_list


# Jika dijalankan sebagai file utama, tes fungsi
if __name__ == "__main__":
    hasil_teks = recognize_speech()
    print("Hasil Speech-to-Text:", hasil_teks)

