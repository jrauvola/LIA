import React, { useState, useRef } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import Recorder from 'recorder-js';

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

const Audio = styled.audio`
  margin-top: 20px;
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
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState('');
  const [videoUrl, setVideoUrl] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [question, setQuestion] = useState("Hi I'm Lia! Let's get started. Tell me a little about yourself!");
  const videoRef = useRef();
  const audioRef = useRef();
  const audioContext = useRef(null);
  const recorder = useRef(null);
  const audioBlob = useRef(null);

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
      const videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
      const audioStream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1 } }); // Set channelCount to 1 for mono

      videoRef.current.srcObject = videoStream;
      videoRef.current.play();

      const videoRecorder = new MediaRecorder(videoStream, { mimeType: 'video/webm' });

      const videoChunks = [];

      videoRecorder.ondataavailable = (e) => videoChunks.push(e.data);

      videoRecorder.onstop = () => {
        const videoBlob = new Blob(videoChunks, { type: 'video/webm' });
        const videoUrl = URL.createObjectURL(videoBlob);
        setVideoUrl(videoUrl);
      };

      audioContext.current = new (window.AudioContext || window.webkitAudioContext)();
      recorder.current = new Recorder(audioContext.current, {
        onAnalysed: data => {},
      });
      // Set the number of channels to 1 for mono
      recorder.current.numChannels = 1;

      recorder.current.init(audioStream)
        .then(() => {
          recorder.current.start();
          setIsRecording(true);
        })
        .catch(err => console.log('Uh oh... unable to get stream...', err));

      videoRecorder.start();
    } catch (err) {
      setError('Cannot access media devices. Make sure to give permission.');
      console.error('Error starting recording:', err);
    }
  };

  const stopRecording = async (videoChunks) => {
    console.log('Stopping media tracks and clearing video source');

    videoRef.current.srcObject.getTracks().forEach((track) => {
      track.stop();
      console.log('Stopped media track:', track);
    });
    videoRef.current.srcObject = null;

    console.log('Stopping audio recorder');

    recorder.current.stop()
      .then(({ blob, buffer }) => {
        audioBlob.current = blob;
        const audioUrl = URL.createObjectURL(blob);
        setAudioUrl(audioUrl);
        console.log('Recording stopped successfully. Blob available:', !!blob);

        // Convert videoChunks to an array
        const videoChunksArray = Array.from(videoChunks);

        // Convert videoChunksArray to an array of Blob objects
        const blobChunks = videoChunksArray.map(chunk => new Blob([chunk], { type: 'video/webm' }));

        // Create a new Blob from the blobChunks array
        const videoBlob = new Blob(blobChunks, { type: 'video/webm' });
        uploadToGCP(videoBlob, audioBlob.current);
      })
      .catch(error => {
        console.error('Error stopping recording:', error);
      });

    setIsRecording(false);
  };

  const uploadToGCP = async (videoBlob, audioBlob) => {
    try {
      console.log('Starting file upload to GCP...');

      const formData = new FormData();
      formData.append('video', videoBlob, 'video.webm');
      formData.append('audio', audioBlob, 'audio.wav');

      console.log('Sending POST request to /stop_recording endpoint...');

      const response = await axios.post('http://127.0.0.1/stop_recording', formData, {
        withCredentials: true,
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      console.log('Response received from /stop_recording endpoint:', response.data);

      // Handle the response and update the question if needed
      if (response.data.nextQuestion) {
        setQuestion(response.data.nextQuestion);
      }

      if (response.data.videoUrl) {
        console.log('Video URL received:', response.data.videoUrl);
        setVideoUrl(response.data.videoUrl);
      }

      if (response.data.audioUrl) {
        console.log('Audio URL received:', response.data.audioUrl);
        setAudioUrl(response.data.audioUrl);
      }

      console.log('File upload to GCP completed successfully.');
    } catch (error) {
      console.error('Error uploading media:', error.message);
    }
  };

    const playback = () => {
    videoRef.current.play();
    audioRef.current.play();
  };

  return (
    <Container>
      <VideoContainer>
        <Video ref={videoRef} playsInline src={videoUrl} />
        <Audio ref={audioRef} src={audioUrl} />
        {error && <p>Error: {error}</p>}
        {isRecording ? (
          <Button onClick={stopRecording}>Stop Recording</Button>
        ) : (
          <Button onClick={startRecording}>Start Recording</Button>
        )}
        {videoUrl && audioUrl && <Button onClick={playback}>Playback</Button>}
      </VideoContainer>
      <QuestionContainer>
        <QuestionText>{question}</QuestionText>
      </QuestionContainer>
    </Container>
  );
}

export default Chatbot;