import React, { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client"; // Import io from socket.io-client

function SpeechToSign() {
  const [currentSentence] = useState("");
  const [status, setStatus] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [micStatus, setMicStatus] = useState("");
  const recognitionTimeout = useRef(null);

  // Initialize the socket connection
  const socket = io("http://localhost:3000"); // Replace with your server URL

  useEffect(() => {
    const currentTimeout = recognitionTimeout.current;
    return () => {
      clearTimeout(currentTimeout);
    };
  }, []);

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

  const checkMicStatus = async () => {
    if (isListening) {
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

  // Ensure that 'isListening' is included in the useEffect dependency array
  useEffect(() => {
    if (isListening) {
      checkMicStatus();
    }
  }, [isListening]); // Add 'isListening' as a dependency

  return (
    <div>
      <h2>Speech-to-Text Converter</h2>
      <button onClick={startListening} disabled={isListening}>
        Mulai Mendengarkan
      </button>
      <button onClick={stopListening} disabled={!isListening}>
        Stop Mendengarkan
      </button>

      <div>
        <p><strong>Status: </strong>{status}</p>
        <p><strong>Status Mikrofon: </strong>{micStatus}</p>
      </div>

      <div style={{ marginTop: "20px", padding: "10px", border: "1px solid #ccc" }}>
        <strong>Kalimat yang Diterima: </strong>{currentSentence}
      </div>
    </div>
  );
}

export default SpeechToSign;
