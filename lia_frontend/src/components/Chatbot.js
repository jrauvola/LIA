import React, { useState, useRef, useEffect } from 'react';
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { fetchFile } from '@ffmpeg/util';
import './Chatbot.css';

function Chatbot() {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState('');
  const [mediaUrl, setMediaUrl] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [question, setQuestion] = useState("Hi I'm Lia! Let's get started. Tell me a little about yourself!");
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [processingDuration, setProcessingDuration] = useState(0);
  const [ffmpegLoaded, setFfmpegLoaded] = useState(false);
  const videoRef = useRef();
  const mediaRecorderRef = useRef();
  const recordedChunksRef = useRef([]);
  const ffmpegRef = useRef(new FFmpeg({ log: true }));
  const recordingTimerRef = useRef(null);

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

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsRecording(false);
    stopRecordingTimer();
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
    const audioUrl = URL.createObjectURL(audioBlob);
    setAudioUrl(audioUrl);
    console.log('WAV file created, audio URL:', audioUrl);

    // Clean up - need to look into more
    // await ffmpeg.unlink(webmFilename);
    // await ffmpeg.unlink(wavFilename);
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








