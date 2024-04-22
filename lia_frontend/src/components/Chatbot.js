// Chatbot.js
import React, { useState, useRef } from 'react';
import axios from 'axios';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const Video = styled.video`
  width: 90%; // Or set to a fixed size
  border-radius: 20px;
  margin-bottom: 20px;
`;

const Button = styled.button`
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #4caf50;
  color: white;
  font-size: 16px;
  cursor: pointer;
  margin: 5px;
  
  &:hover {
    background-color: #45a049;
  }
  
  &:disabled {
    background-color: #ccc;
    cursor: default;
  }
`;

function Chatbot() {
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState('');
  const videoRef = useRef();

  // Function to start recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      videoRef.current.srcObject = stream;
      const recorder = new MediaRecorder(stream);
      recorder.ondataavailable = async (e) => {
        const blob = new Blob([e.data], { type: 'video/webm' });
        const formData = new FormData();
        formData.append('file', blob, 'recording.webm');
        await axios.post('http://localhost:5000/upload_video', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      };
      setIsRecording(true);
      recorder.start();
    } catch (err) {
      setError('Cannot access media devices. Make sure to give permission.');
      console.error('Error starting recording:', err);
    }
  };

  // Function to stop recording
  const stopRecording = () => {
    // stop the MediaRecorder instance and the video stream
    setIsRecording(false);
    videoRef.current.srcObject.getTracks().forEach(track => track.stop());
    //Close the video and display the recorded video
    videoRef.current.srcObject = null;

    //Display the recorded video in the same page
    const recordedVideo = document.createElement('video');
    recordedVideo.controls = true;
    document.body.appendChild(recordedVideo);

    // Save the recorded video to a file
    const downloadButton = document.createElement('button');
    downloadButton.textContent = 'Download';
    document.body.appendChild(downloadButton);

    downloadButton.addEventListener('click', () => {
      const a = document.createElement('a');
      a.href = recordedVideo.src;
      a.download = 'recording.webm';
      a.click();
    });

  };

  // Function to handle file upload to GCP
  const uploadToGCP = async (blob) => {
    // Code to handle file upload
  };

  return (
    <Container>
      <Video ref={videoRef} autoPlay playsInline />
      {error && <p>Error: {error}</p>}
      {isRecording ? (
        <Button onClick={stopRecording}>Stop Recording</Button>
      ) : (
        <Button onClick={startRecording}>Start Recording</Button>
      )}
    </Container>
  );
}

export default Chatbot;




// # Original start recording
  // // Function to start recording
  // const startRecording = async () => {
  //   try {
  //     const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  //     videoRef.current.srcObject = stream;
  //     const recorder = new MediaRecorder(stream);
  //     recorder.ondataavailable = (e) => {
  //       const blob = new Blob([e.data], { type: 'video/webm' });
  //       uploadToGCP(blob);
  //     };
  //     setIsRecording(true);
  //     recorder.start();

  //     // Save the recorded chunks
  //     const recordedChunks = [];
  //     recorder.ondataavailable = e => recordedChunks.push(e.data);


  //   } catch (err) {
  //     setError('Cannot access media devices. Make sure to give permission.');
  //     console.error('Error starting recording:', err);
  //   }
  // };
