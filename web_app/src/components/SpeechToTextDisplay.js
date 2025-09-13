import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SpeechToTextDisplay = () => {
  const [text, setText] = useState("");

  // Mengambil teks dari backend setiap beberapa detik
  useEffect(() => {
    const interval = setInterval(() => {
      axios.get("http://localhost:5000/get-latest-text")  // Ganti dengan URL endpoint backend Anda
        .then(response => {
          setText(response.data.text);
        })
        .catch(error => {
          console.error("Error fetching text:", error);
        });
    }, 1000);  // Cek setiap detik

    return () => clearInterval(interval);  // Bersihkan interval saat komponen di-unmount
  }, []);

  return (
    <div>
      <h2>Kalimat yang Terdeteksi:</h2>
      <p>{text}</p>
    </div>
  );
};

export default SpeechToTextDisplay;
