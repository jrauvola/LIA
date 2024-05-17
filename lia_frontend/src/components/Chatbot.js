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
  

// Function to make the API request to display the next question
const displayQuestionAPI = async () => {
  try {
    const response = await axios.post('http://127.0.0.1/display_question', null, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    console.log('Question received successfully:', response.data);

    if (response.data.nextQuestion) {
      setQuestion(response.data.nextQuestion);
    } else {
      console.log('No next question available');
    }
  } catch (error) {
    console.error('Error receiving question:', error);
    // Handle the error as needed
  }
};

// Function to make the API request to generate the next question
const generateQuestionAPI = async () => {
  try {
    await axios.post('http://127.0.0.1/generate_question', null, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    console.log('Question generation triggered successfully');
  } catch (error) {
    console.error('Error triggering question generation:', error);
    // Handle the error as needed
  }
};
  
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

      // Call the API request function to display the question
      await displayQuestionAPI();

      // Call the API request function to generate the next question
      await generateQuestionAPI();

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
      console.log('Starting file upload to GCP...'); // Added logging statement

      const formData = new FormData();
      formData.append('file', blob, 'recording.webm');

      console.log('Sending POST request to /user_recording endpoint...'); // Added logging statement

      const response = await axios.post('http://127.0.0.1/stop_recording', formData, {
        withCredentials: true,
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      console.log('Response received from /user_recording endpoint:', response.data); // Added logging statement

      // if (response.data.nextQuestion) {
      //   setQuestion(response.data.nextQuestion); 
      // }

      if (response.data.signedUrl) {
        console.log('Signed URL received:', response.data.signedUrl); // Added logging statement
        setVideoUrl(response.data.signedUrl);
      } else {
        console.error('Error uploading media:', response.data.error);
      }

      console.log('File upload to GCP completed successfully.'); // Added logging statement
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
          <Button onClick={startRecording}>Start Interview</Button>
        )}
      </VideoContainer>
      <QuestionContainer>
        <QuestionText>{question}</QuestionText>
      </QuestionContainer>
    </Container>
  );
}

export default Chatbot;