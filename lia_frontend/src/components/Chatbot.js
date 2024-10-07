import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import RecordRTC from 'recordrtc';
import './Chatbot.css';
import axios from "axios";

function Chatbot() {
  const [isRecording, setIsRecording] = useState(false);
  const [isSoundcheck, setIsSoundcheck] = useState(false);
  const [error, setError] = useState('');
  const [mediaUrl, setMediaUrl] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [question, setQuestion] = useState("Hi I'm Lia! Let's get started. Tell me a little about yourself!");
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [processingDuration, setProcessingDuration] = useState(0);
  const [questionCount, setQuestionCount] = useState(0);
  const videoRef = useRef();
  const recorderRef = useRef(null);
  const recordingTimerRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const mediaRecorderRef = useRef(null);
  const navigate = useNavigate();

  const generateQuestionAPI = async () => {
    try {
      const response = await axios.post('http://127.0.0.1/generate_question', null, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      console.log('Question generation triggered successfully');
      setQuestionCount(prev => prev + 1);
    } catch (error) {
      console.error('Error triggering question generation:', error);
    }
  };

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
    }
  };

  const startRecordingTimer = () => {
    // Clear any existing interval before starting a new one
    clearInterval(recordingTimerRef.current);
    recordingTimerRef.current = setInterval(() => {
      setRecordingDuration(prev => prev + 1);
    }, 1000);
  };

  const stopRecordingTimer = () => {
    clearInterval(recordingTimerRef.current);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 48000,
          channelCount: 1
        }
      });
      videoRef.current.srcObject = stream;

      // Mute the video track
      videoRef.current.muted = true;
      videoRef.current.volume = 0;

      recorderRef.current = new RecordRTC(stream, {
        type: 'video',
        mimeType: 'video/webm',
        recorderType: RecordRTC.MediaStreamRecorder,
        videoBitsPerSecond: 128000,
        audioBitsPerSecond: 128000,
        audioChannels: 1,
        sampleRate: 48000
      });

      recorderRef.current.startRecording();
      setIsRecording(true);
      await generateQuestionAPI();
      setRecordingDuration(0); // Reset the timer to zero before starting
      startRecordingTimer();
    } catch (err) {
      setError('Failed to start recording: ' + err.message);
      console.error('Error starting recording:', err);
    }
  };

  const stopRecording = async () => {
    if (recorderRef.current) {
      recorderRef.current.stopRecording(() => {
        const blob = recorderRef.current.getBlob();
        const mediaUrl = URL.createObjectURL(blob);
        setMediaUrl(mediaUrl);
        uploadToGCP(blob);
      });
    }
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;  

    }
    setIsRecording(false);
    stopRecordingTimer();
  };

  const uploadToGCP = async (blob) => {
    try {
      console.log('Starting file upload to GCP...');

      const formData = new FormData();
      formData.append('video', blob, 'video.webm');

      console.log('Sending POST request to /stop_recording endpoint...');

      const response = await axios.post('http://127.0.0.1/stop_recording', formData, {
        withCredentials: true,
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      console.log('Response received from /stop_recording endpoint:', response.data);

      if (response.data.mediaUrl) {
        console.log('Video URL received:', response.data.mediaUrl);
        setMediaUrl(response.data.mediaUrl);
      }

      console.log('File upload to GCP completed successfully.');
    } catch (error) {
      console.error('Error uploading media:', error.message);
    }
  };

  const handleEvaluation = async () => {
    try {
      const response = await axios.post('http://127.0.0.1/print_evaluate', null, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      console.log('Evaluator received successfully:', response.data);

      if (response.data.nextQuestion) {
        setQuestion(response.data.nextQuestion);
      } else {
        console.log('No evaluator available');
      }
    } catch (error) {
      console.error('Error receiving evaluator:', error);
    }
  };

  const startSoundcheck = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      recordedChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => recordedChunksRef.current.push(e.data);

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(recordedChunksRef.current, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioUrl(audioUrl);
        console.log('Soundcheck recording stopped, audio URL created:', audioUrl);
        setIsSoundcheck(false);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsSoundcheck(true);
      setTimeout(() => {
        mediaRecorder.stop();
        stream.getTracks().forEach(track => track.stop());
      }, 3000); // Record for 3 seconds
    } catch (err) {
      setError('Failed to start soundcheck: ' + err.message);
      console.error('Error starting soundcheck:', err);
    }
  };

  return (
    <div className="container">
      <div className="video-container">
        <video className="video" ref={videoRef} autoPlay playsInline />
        {error && <p>Error: {error}</p>}
        <div className="timer">
          <p>Questions Generated: {questionCount}</p>
          <p>Recording Duration: {recordingDuration}s</p>
          {processingDuration > 0 && <p>Processing Duration: {processingDuration}s</p>}
        </div>
        {isRecording ? (
          <button className="button" onClick={stopRecording}>Stop Recording</button>
        ) : (
          <button
              className="button"
              onClick={async () => {
                setRecordingDuration(0); // Reset the timer to zero
                await displayQuestionAPI();
                setTimeout(() => {
                  startRecording();
                }, 1000); // 1-second delay
              }}
          >
            Start Recording
          </button>
        )}
        <button className="button" onClick={handleEvaluation}>Get Evaluation</button>
        <button className="button" onClick={startSoundcheck}>
          {isSoundcheck ? 'Recording Soundcheck...' : 'Start Soundcheck'}
        </button>
      </div>
      <div className="question-container">
        <img className="lia-image" src="/LIA.webp" alt="LIA" />
        <p className="question-text">{question}</p>
      </div>
      {audioUrl && (
        <div className="audio-container">
          <audio controls src={audioUrl}></audio>
          <p>Can you hear this audio? If not, please check your microphone settings.</p>
        </div>
      )}
    </div>
  );
}

export default Chatbot;