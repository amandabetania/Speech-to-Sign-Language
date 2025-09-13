import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [status, setStatus] = useState('Idle'); // Status program (Idle, Running, Stopped)
  const [recognitionStatus, setRecognitionStatus] = useState('Waiting for input...');
  const [text, setText] = useState('');
  const [videoUrls, setVideoUrls] = useState([]);

  // Fungsi untuk memulai speech recognition
  const startRecognition = async () => {
    try {
      const response = await axios.post('http://localhost:5000/start');
      setStatus('Running');
      setRecognitionStatus('Listening...');
    } catch (error) {
      console.error("Error starting recognition:", error);
      setRecognitionStatus('Error starting recognition');
    }
  };

  // Fungsi untuk menghentikan speech recognition
  const stopRecognition = async () => {
    try {
      const response = await axios.post('http://localhost:5000/stop');
      setStatus('Stopped');
      setRecognitionStatus('Recognition stopped');
    } catch (error) {
      console.error("Error stopping recognition:", error);
      setRecognitionStatus('Error stopping recognition');
    }
  };

  // Fungsi untuk mengambil hasil (teks dan video)
  const fetchResults = async () => {
    try {
      const response = await axios.get('http://localhost:5000/get_results');
      const data = response.data;
      setText(data.text);
      setVideoUrls(data.videoUrls); // Misalnya { text: "Halo", videoUrls: ["video1.webm", "video2.webm"] }
    } catch (error) {
      console.error("Error fetching results:", error);
      setRecognitionStatus('Error fetching results');
    }
  };

  return (
    <div className="App">
      <h1>Speech to Sign Language</h1>
      <div>
        <button onClick={startRecognition} disabled={status === 'Running'}>
          Start
        </button>
        <button onClick={stopRecognition} disabled={status === 'Stopped'}>
          Stop
        </button>
      </div>

      <div>
        <h3>Status: {status}</h3>
        <p>Recognition Status: {recognitionStatus}</p>
      </div>

      <div>
        <h3>Detected Text:</h3>
        <p>{text}</p>
      </div>

      <div>
        <h3>Sign Language Videos:</h3>
        {videoUrls.map((url, index) => (
          <video key={index} width="320" height="240" controls>
            <source src={`http://localhost:5000/${url}`} type="video/webm" />
            Your browser does not support the video tag.
          </video>
        ))}
      </div>
    </div>
  );
};

export default App;
