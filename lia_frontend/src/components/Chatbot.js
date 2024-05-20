import React, { useState, useRef, useEffect } from 'react';
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { fetchFile } from '@ffmpeg/util';
import './Chatbot.css';
import axios from "axios";

function Chatbot() {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState('');
  const [mediaUrl, setMediaUrl] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [question, setQuestion] = useState("Hi I'm Lia! Let's get started. Tell me a little about yourself!");
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [processingDuration, setProcessingDuration] = useState(0);
  const [ffmpegLoaded, setFfmpegLoaded] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);  // New state variable
  const videoRef = useRef();
  const mediaRecorderRef = useRef();
  const recordedChunksRef = useRef([]);
  const ffmpegRef = useRef(new FFmpeg({ log: true }));
  const recordingTimerRef = useRef(null);

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

  const loadFFmpeg = async () => {
    const ffmpeg = ffmpegRef.current;
    if (!ffmpegLoaded) {
      await ffmpeg.load();
      setFfmpegLoaded(true);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      videoRef.current.srcObject = stream;

      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
      recordedChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => recordedChunksRef.current.push(e.data);

      mediaRecorder.onstop = async () => {
        const mediaBlob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
        const mediaUrl = URL.createObjectURL(mediaBlob);
        setMediaUrl(mediaUrl);
        console.log('Recording stopped, media URL created:', mediaUrl);

        // Start processing timer
        const startTime = Date.now();
        await loadFFmpeg();
        await convertToWav(mediaBlob);
        const endTime = Date.now();
        setProcessingDuration(((endTime - startTime) / 1000).toFixed(2));
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      startRecordingTimer();
    } catch (err) {
      setError('Failed to start recording: ' + err.message);
      console.error('Error starting recording:', err);
    }
  };

  const stopRecording = async () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsRecording(false);
    stopRecordingTimer();

    // Get the video and audio blobs
    const videoBlob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
    // Ensure audioBlob is available before uploading
    const checkAudioBlobReady = () => {
      if (audioBlob) {
        uploadToGCP(videoBlob, audioBlob);
      } else {
        setTimeout(checkAudioBlobReady, 100);
      }
    };

    checkAudioBlobReady();
  };

  const startRecordingTimer = () => {
    setRecordingDuration(0);
    recordingTimerRef.current = setInterval(() => {
      setRecordingDuration((prevDuration) => prevDuration + 1);
    }, 1000);
  };

  const stopRecordingTimer = () => {
    clearInterval(recordingTimerRef.current);
  };

  const convertToWav = async (mediaBlob) => {
    const ffmpeg = ffmpegRef.current;
    const webmFilename = 'recording.webm';
    const wavFilename = 'recording.wav';

    // Load the media file into ffmpeg
    await ffmpeg.writeFile(webmFilename, await fetchFile(mediaBlob));

    // Run the conversion command
    await ffmpeg.exec(['-i', webmFilename, wavFilename]);

    // Read the result
    const data = await ffmpeg.readFile(wavFilename);
    const audioBlob = new Blob([data.buffer], { type: 'audio/wav' });
    setAudioBlob(audioBlob); // this is necessary to make sure the same audio file is downloading and going to bucket
    const audioUrl = URL.createObjectURL(audioBlob);
    setAudioUrl(audioUrl);
    console.log('WAV file created, audio URL:', audioUrl);
    const videoBlob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
    await uploadToGCP(videoBlob, audioBlob);
    // const audioUrl = URL.createObjectURL(audioBlob);
    // setAudioUrl(audioUrl);
    // console.log('WAV file created, audio URL:', audioUrl);
    //
    // // Clean up - need to look into more
    // await ffmpeg.unlink(webmFilename);
    // await ffmpeg.unlink(wavFilename);
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
        console.log('Next question received:', response.data.nextQuestion);
        setQuestion(response.data.nextQuestion);
      } else {
        console.log('No next question in response.');
      }

      if (response.data.mediaUrl) {
        console.log('Video URL received:', response.data.mediaUrl);
        setMediaUrl(response.data.mediaUrl);
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

  return (
    <div className="container">
      <div className="video-container">
        <video className="video" ref={videoRef} autoPlay playsInline />
        {error && <p>Error: {error}</p>}
        <div className="timer">
          <p>Recording Duration: {recordingDuration}s</p>
          {processingDuration > 0 && <p>Processing Duration: {processingDuration}s</p>}
        </div>
        {isRecording ? (
          <button className="button" onClick={stopRecording}>Stop Recording</button>
        ) : (
          <button className="button" onClick={startRecording}>Start Recording</button>
        )}
        {mediaUrl && (
          <div>
            <video controls src={mediaUrl} className="recorded-video"></video>
            <a href={mediaUrl} download="recorded-video.webm">Download Video</a>
          </div>
        )}
        {audioUrl && (
          <div>
            <audio controls src={audioUrl} className="recorded-audio"></audio>
            <a href={audioUrl} download="recorded-audio.wav">Download Audio</a>
          </div>
        )}
      </div>
      <div className="question-container">
        <img className="lia-image" src="/LIA.webp" alt="LIA" />
        <p className="question-text">{question}</p>
      </div>
    </div>
  );
}

export default Chatbot;








