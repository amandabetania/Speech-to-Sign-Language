import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { io } from 'socket.io-client';

const SignLanguageVideos = ({ text }) => {
  const [videos, setVideos] = useState([]);
  const [status, setStatus] = useState('');
  const [micStatus, setMicStatus] = useState('');
  const [isListening, setIsListening] = useState(false);
  const socket = io("http://localhost:3000");  // Ganti dengan URL server Anda
  const recognitionTimeout = useRef(null);

  // Initialize video fetching based on text
  useEffect(() => {
    if (text) {
      setStatus("Start Processing");
      axios.post("http://localhost:3000/get-sign-language-videos", { text })
        .then(response => {
          setVideos(response.data.videos);
        })
        .catch(error => {
          console.error("Error fetching videos:", error);
        });
    }
  }, [text]);

  const startListening = async () => {
    if (socket) {
      socket.emit("start_speech_recognition");
      setStatus("Start Processing");
      setIsListening(true);
      setMicStatus("");

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const detectMicActivity = () => {
          analyser.getByteFrequencyData(dataArray);
          const volume = dataArray.reduce((acc, curr) => acc + curr, 0) / dataArray.length;
          if (volume > 10) {
            setMicStatus("Mikrofon mendeteksi suara...");
          } else {
            setMicStatus("Mikrofon tidak mendeteksi suara");
          }
          requestAnimationFrame(detectMicActivity);
        };
        detectMicActivity();
      } catch (err) {
        console.error("Error accessing microphone:", err);
        setMicStatus("Mikrofon tidak tersedia");
      }
    }
  };

  const stopListening = () => {
    if (socket) {
      socket.emit("stop_speech_recognition");
      setStatus("Stop Processing");
      setMicStatus("Mikrofon berhenti menangkap suara");
      setIsListening(false);
    }
  };

  return (
    <div>
      <h2>Speech-to-Text & Video Bahasa Isyarat</h2>
      <div>
        <button onClick={startListening} disabled={isListening}>
          Mulai Mendengarkan
        </button>
        <button onClick={stopListening} disabled={!isListening}>
          Stop Mendengarkan
        </button>
      </div>

      <div>
        <p><strong>Status: </strong>{status}</p>
        <p><strong>Status Mikrofon: </strong>{micStatus}</p>
      </div>

      <h3>Video Bahasa Isyarat:</h3>
      {videos.length > 0 ? (
        videos.map((video, index) => (
          <div key={index}>
            <video controls width="320">
              <source src={`http://localhost:5000/videos/${video}`} type="video/webm" />
              Your browser does not support the video tag.
            </video>
          </div>
        ))
      ) : (
        <p>Menunggu video...</p>
      )}
    </div>
  );
};

export default SignLanguageVideos;
