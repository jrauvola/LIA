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

  const initializeAudioContext = async () => {
    try {
      // Check if AudioContext is supported
      if (!window.AudioContext && !window.webkitAudioContext) {
        throw new Error('Web Audio API is not supported in this browser');
      }

      // Create audio context with error handling
      const context = new (window.AudioContext || window.webkitAudioContext)();
      console.log('Audio Context initialized:', context.state);
      
      // Resume context if it's in suspended state
      if (context.state === 'suspended') {
        await context.resume();
        console.log('Audio Context resumed');
      }
      
      return context;
    } catch (error) {
      console.error('Failed to initialize audio context:', error);
      throw error;
    }
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

      // Initialize audio context
      const context = await initializeAudioContext();
      console.log('Audio context created:', context);
      
      const source = context.createMediaStreamSource(stream);
      console.log('Media stream source created:', source);
      
      const analyser = context.createAnalyser();
      analyser.fftSize = 2048;
      analyser.minDecibels = -90;
      analyser.maxDecibels = -10;
      analyser.smoothingTimeConstant = 0.85;
      
      source.connect(analyser);
      console.log('Audio analysis chain connected');
      
      setAudioContext(context);
      setAudioAnalyser(analyser);
      
      // Start the analysis loop
      requestAnimationFrame(analyzeAudio);

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
      console.error('Recording setup failed:', err);
      if (err.name === 'NotAllowedError') {
        setError('Please grant microphone and camera permissions');
      } else {
        setError(`Failed to start recording: ${err.message}`);
      }
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
    
    // Increment attempt count and check if we should navigate
    const newCount = attemptCount + 1;
    setAttemptCount(newCount);
    if (newCount > 5) {
      navigate('/evaluation');
    }
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

  const analyzeAudio = () => {
    if (!isRecording || !audioAnalyser) {
      console.log('Audio analyser not available or recording stopped, stopping audio analysis');
      return;
    }

    try {
      const dataArray = new Uint8Array(audioAnalyser.frequencyBinCount);
      audioAnalyser.getByteFrequencyData(dataArray);

      const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      const scaledLevel = Math.min(Math.max((average / 255) * 100, 0), 100);

      console.log(`Average Frequency: ${average}, Scaled Level: ${scaledLevel}`);

      setAudioLevel(scaledLevel);

      animationFrameRef.current = requestAnimationFrame(analyzeAudio);
    } catch (error) {
      console.error('Error in analyzeAudio:', error);
    }
  };

  useEffect(() => {
    console.log('Audio context state changed:', audioContext);
  }, [audioContext]);

  useEffect(() => {
    console.log('Audio analyser state changed:', audioAnalyser);
  }, [audioAnalyser]);

  useEffect(() => {
    console.log('Audio level updated:', audioLevel);
  }, [audioLevel]);

  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContext) {
        audioContext.close();
      }
    };
  }, []);

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
          <div className="recording-bar">
            <div className="recording-indicator"></div>
            <span className="recording-time">{recordingDuration}s</span>
            <button className="button" onClick={stopRecording}>Stop</button>
          </div>
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
        <div className="audio-meter-container">
          <div 
            className="audio-meter"
            style={{ 
              height: `${Math.min(audioLevel, 100)}%`
            }}
          />
        </div>
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