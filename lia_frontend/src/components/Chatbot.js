import React, { useState, useRef, useEffect, memo } from 'react';
import { useNavigate } from 'react-router-dom';
import RecordRTC from 'recordrtc';
import './Chatbot.css';
import axios from "axios";
import { v4 as uuidv4 } from 'uuid';
import TypewriterMessage from './TypewriterMessage';
import { FaPlay, FaPause, FaVolumeMute } from 'react-icons/fa';

const ChatMessage = memo(({ role, message, isInterim = false }) => {
  const formatMessage = (msg) => {
    return msg.replace(/^##\s*Technical Interview Question based on Personal Profile:\s*/i, '');
  };

  return (
    <div className={`chat-message ${role} ${isInterim ? 'interim' : ''}`}>
      <div className="message-header">
        {role === 'lia' ? '💃 LIA:' : '👤 User:'}
      </div>
      <div className="message-content">
        {formatMessage(message)}
      </div>
    </div>
  );
});

function Chatbot() {
  const [isRecording, setIsRecording] = useState(false);
  const [isSoundcheck, setIsSoundcheck] = useState(false);
  const [error, setError] = useState('');
  const [mediaUrl, setMediaUrl] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [conversation, setConversation] = useState([]);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [processingDuration, setProcessingDuration] = useState(0);
  const [questionCount, setQuestionCount] = useState(0);
  const [audioContext, setAudioContext] = useState(null);
  const [audioAnalyser, setAudioAnalyser] = useState(null);
  const [audioLevel, setAudioLevel] = useState(0);
  const [attemptCount, setAttemptCount] = useState(0);
  const videoRef = useRef();
  const recorderRef = useRef(null);
  const recordingTimerRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const mediaRecorderRef = useRef(null);
  const navigate = useNavigate();
  const animationFrameRef = useRef(null);
  const chatContainerRef = useRef(null);
  const [typingMessage, setTypingMessage] = useState(null);
  const [interimTranscript, setInterimTranscript] = useState('');
  const [liveTranscript, setLiveTranscript] = useState('');
  const [showStartPrompt, setShowStartPrompt] = useState(true);
  const [currentVideo, setCurrentVideo] = useState('appearing');
  const liaVideoRef = useRef(null);

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

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
        const cleanedQuestion = response.data.nextQuestion
          .replace(/\*\*/g, '')
          .trim();
        
        setConversation(prev => [
          ...prev, 
          { 
            id: uuidv4(),
            role: 'lia', 
            message: cleanedQuestion 
          }
        ]);
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
      setShowStartPrompt(false);
      console.log('🎥 startRecording: Requesting media permissions');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          channelCount: 1,
          sampleRate: 16000,
          sampleSize: 16
        }
      });
      
      console.log('Stream tracks:', stream.getTracks().map(track => ({
        kind: track.kind,
        enabled: track.enabled,
        muted: track.muted,
        readyState: track.readyState
      })));

      videoRef.current.srcObject = stream;
      console.log('Video source object set:', videoRef.current.srcObject !== null);

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
      
      // Start analysis with proper reference
      animationFrameRef.current = requestAnimationFrame(analyzeAudio);

      // Mute the video track
      videoRef.current.muted = true;
      videoRef.current.volume = 0;
      console.log('🎬 startRecording: Initializing RecordRTC');
      console.log('🎬 startRecording: RecordRTC configuration:', {
        type: 'video',
        mimeType: 'video/webm',
        numberOfAudioChannels: 1,
        desiredSampRate: 16000,
        bufferSize: 4096
      });

      recorderRef.current = new RecordRTC(stream, {
        type: 'video',
        mimeType: 'video/webm',
        recorderType: RecordRTC.MediaStreamRecorder,
        numberOfAudioChannels: 1,
        desiredSampRate: 16000,
        bufferSize: 4096
      });

      console.log('Recorder state before starting:', recorderRef.current.getState());
      recorderRef.current.startRecording();
      console.log('Recorder state after starting:', recorderRef.current.getState());
      setIsRecording(true);
      setRecordingDuration(0);
      startRecordingTimer();
    } catch (err) {
      console.error('❌ startRecording: Error:', err);
      if (err.name === 'NotAllowedError') {
        setError('Please grant microphone and camera permissions');
      } else {
        setError(`Failed to start recording: ${err.message}`);
      }
    }
  };

  const stopRecording = async () => {
    console.log('Stopping recording...');
    if (recorderRef.current) {
      console.log('Recorder state before stopping:', recorderRef.current.getState());
      
      recorderRef.current.stopRecording(() => {
        const blob = recorderRef.current.getBlob();
        console.log('Recording stopped, blob size:', blob.size);
        console.log('Blob type:', blob.type);
        
        const mediaUrl = URL.createObjectURL(blob);
        setMediaUrl(mediaUrl);
        
        // Log the tracks before stopping them
        if (videoRef.current && videoRef.current.srcObject) {
          const tracks = videoRef.current.srcObject.getTracks();
          console.log('Tracks before stopping:', tracks.map(track => ({
            kind: track.kind,
            enabled: track.enabled,
            readyState: track.readyState
          })));
        }
        
        uploadToGCP(blob);
      });
    } else {
      console.warn('No recorder reference found when stopping recording');
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
    if (newCount > 4) {
      navigate('/evaluation');
    }
  };

  const uploadToGCP = async (blob) => {
    try {
      console.log('Starting file upload to GCP...');
      console.log('Blob details:', {
        size: blob.size,
        type: blob.type
      });

      const formData = new FormData();
      formData.append('video', blob, 'video.webm');
      
      console.log('FormData created with video blob');

      const response = await axios.post('http://127.0.0.1/stop_recording', formData, {
        withCredentials: true,
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      console.log('Upload response:', response.data);

      if (response.data.transcript) {
        const userMessage = {
          id: uuidv4(),
          role: 'user',
          message: response.data.transcript
        };
        setConversation(prev => [...prev, userMessage]);
        
        setLiveTranscript('');
      }

      if (response.data.mediaUrl) {
        console.log('Video URL received:', response.data.mediaUrl);
        setMediaUrl(response.data.mediaUrl);
      }

      await generateQuestionAPI();

      console.log('File upload to GCP completed successfully.');
    } catch (error) {
      console.error('Upload error:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data
      });
      setError('Failed to upload recording');
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

      // Update this line to use .current
      animationFrameRef.current = requestAnimationFrame(analyzeAudio);
    } catch (error) {
      console.error('Error in analyzeAudio:', error);
    }
  };

  // Your useEffect hooks for logging
  useEffect(() => {
    console.log('Audio context state changed:', audioContext);
  }, [audioContext]);

  useEffect(() => {
    console.log('Audio analyser state changed:', audioAnalyser);
  }, [audioAnalyser]);

  useEffect(() => {
    console.log('Audio level updated:', audioLevel);
  }, [audioLevel]);

    // Modified cleanup useEffect
    useEffect(() => {
      return () => {
        // Cleanup animation frame
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }

        // Cleanup audio context
        if (audioContext) {
          audioContext.close().catch(err => {
            console.error('Error closing audio context:', err);
          });
        }

        // Clean up media stream
        if (videoRef.current && videoRef.current.srcObject) {
          const tracks = videoRef.current.srcObject.getTracks();
          tracks.forEach(track => track.stop());
          videoRef.current.srcObject = null;
        }
      };
    }, []);

  useEffect(() => {
    const liaVideo = liaVideoRef.current;
    
    const handleVideoEnd = () => {
      if (currentVideo === 'appearing') {
        setCurrentVideo('waving');
      } else if (currentVideo === 'waving') {
        setCurrentVideo('staying');
      }
    };

    if (liaVideo) {
      liaVideo.addEventListener('ended', handleVideoEnd);
    }

    return () => {
      if (liaVideo) {
        liaVideo.removeEventListener('ended', handleVideoEnd);
      }
    };
  }, [currentVideo]);

  const getCurrentVideoSrc = () => {
    switch(currentVideo) {
      case 'appearing':
        return '/videos/lia_appearing.mp4';
      case 'waving':
        return '/videos/lia_waving.mp4';
      case 'staying':
        return '/videos/lia_staying.mp4';
      default:
        return '/videos/lia_staying.mp4';
    }
  };

  const addMessage = (role, message) => {
    setConversation(prev => [
      ...prev, 
      { id: uuidv4(), role, message }
    ]);
  };

  return (
    <div className="container">
      <div className="video-container">
        <video 
          ref={liaVideoRef}
          className="lia-video"
          src={getCurrentVideoSrc()}
          autoPlay
          muted
          loop={currentVideo === 'staying'}
        />
        <video 
          className={`user-video-minimized ${isRecording ? 'recording' : ''}`}
          ref={videoRef} 
          autoPlay 
          playsInline 
        />
        {error && <p>Error: {error}</p>}
        <div className="timer">
          <p>Questions Generated: {questionCount}</p>
          <p>Recording Duration: {recordingDuration}s</p>
          {processingDuration > 0 && <p>Processing Duration: {processingDuration}s</p>}
        </div>
        <div className="video-controls">
          <div className="recording-controls-bar">
            {isRecording ? (
              <>
                <button className="control-button" onClick={stopRecording}>
                  <FaPause />
                </button>
                <button 
                  className="record-button"
                  onClick={stopRecording}
                />
              </>
            ) : (
              <>
                <button 
                  className="control-button"
                  onClick={async () => {
                    setRecordingDuration(0);
                    await displayQuestionAPI();
                    startRecording();
                  }}
                >
                  <FaPlay />
                </button>
                <button className="record-button" />
              </>
            )}
            <button className="control-button">
              <FaVolumeMute />
            </button>
            <span className="timer-display">
              {String(Math.floor(recordingDuration / 60)).padStart(2, '0')}:
              {String(recordingDuration % 60).padStart(2, '0')}:
              {String(Math.floor((recordingDuration * 100) % 100)).padStart(2, '0')}
            </span>
          </div>
        </div>
      </div>
      <div className="chat-container" ref={chatContainerRef}>
        <img className="lia-image" src="/LIA.webp" alt="LIA" />
        <div className="messages">
          {showStartPrompt ? (
            <div className="start-prompt">
              To Start your interview press the start button in the middle of the chatbot area
            </div>
          ) : (
            <>
              {conversation.map((msg) => (
                <ChatMessage 
                  key={msg.id}
                  role={msg.role}
                  message={msg.message}
                />
              ))}
              {liveTranscript && isRecording && (
                <ChatMessage
                  key="live-transcript"
                  role="user"
                  message={liveTranscript}
                  isInterim={true}
                />
              )}
            </>
          )}
        </div>
        <div className="chat-controls">
          {/* Any additional chat controls can go here */}
        </div>
      </div>
    </div>
  );
}

export default Chatbot;