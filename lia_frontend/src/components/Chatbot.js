import React, { useState, useRef, useEffect } from 'react';
// import { useLocation } from 'react-router-dom';
import axios from 'axios';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  justify-content: center;
  padding: 20px;
`;

const VideoContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
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

const QuestionContainer = styled.div`
  margin-left: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
`;

const QuestionText = styled.p`
  font-size: 18px;
`;

function Chatbot() {
  // const [recordedChunks, setRecordedChunks] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState('');
  const [videoUrl, setVideoUrl] = useState(null);
  const [question, setQuestion] = useState("Hi I'm Lia! Let's get started. Tell me a little about yourself!");
  const videoRef = useRef();
  // const location = useLocation();
  // const initialQuestion = location.state?.initialQuestion;
  
  // useEffect(() => {
  //   if (initialQuestion) {
  //     setQuestion(initialQuestion);
  //   }
  // }, [initialQuestion]);

  // Function to start recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      videoRef.current.srcObject = stream;
      const videoRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
      const recordedChunks = [];

      videoRecorder.ondataavailable = (e) => recordedChunks.push(e.data);

      videoRecorder.onstop = () => {
        const videoBlob = new Blob(recordedChunks, { type: 'video/webm' });
        const videoUrl = URL.createObjectURL(videoBlob);
        setVideoUrl(videoUrl);
        uploadToGCP(videoBlob);
      };

      setIsRecording(true);
      videoRecorder.start();
    } catch (err) {
      setError('Cannot access media devices. Make sure to give permission.');
      console.error('Error starting recording:', err);
    }
  };

  const stopRecording = async () => {
    videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
    videoRef.current.srcObject = null;
    setIsRecording(false);
  };

  const uploadToGCP = async (blob) => {
    try {
      const formData = new FormData();
      formData.append('file', blob, 'recording.webm');

      const response = await axios.post('https://backend-4e4b4qv3cq-uc.a.run.app/user_recording', formData, {
        withCredentials: true,
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (response.data.nextQuestion) {
        setQuestion(response.data.nextQuestion);
        setIsRecording(false); // Reset recording state
      }

      if (response.data.signedUrl) {
        setVideoUrl(response.data.signedUrl);
      } else {
        console.error('Error uploading media:', response.data.error);
      }
    } catch (error) {
      console.error('Error uploading media:', error.message);
    }
  };

  return (
    <Container>
      <VideoContainer>
        <Video ref={videoRef} autoPlay playsInline src={videoUrl} />
        {error && <p>Error: {error}</p>}
        {isRecording ? (
          <Button onClick={stopRecording}>Stop Recording</Button>
        ) : (
          <Button onClick={startRecording}>Start Recording</Button>
        )}
      </VideoContainer>
      <QuestionContainer>
        <QuestionText>{question}</QuestionText>
      </QuestionContainer>
    </Container>
  );
}

export default Chatbot;
