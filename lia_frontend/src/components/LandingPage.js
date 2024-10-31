import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

function LandingPage() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const [isFading, setIsFading] = useState(false);

  // Memoize triggerFadeOut to prevent unnecessary re-creations
  const triggerFadeOut = useCallback(() => {
    setIsFading(true);
    setTimeout(() => {
      navigate('/about-you');
    }, 1000); // Match the CSS transition duration
  }, [navigate]);

  useEffect(() => {
    const handleVideoEnd = () => {
      triggerFadeOut();
    };

    const videoCurrent = videoRef.current;
    if (videoCurrent) {
      videoCurrent.addEventListener('ended', handleVideoEnd);
      videoCurrent.playbackRate = 0.8; // Slow down the video (e.g., 0.8x speed)
    }

    return () => {
      if (videoCurrent) {
        videoCurrent.removeEventListener('ended', handleVideoEnd);
      }
    };
  }, [triggerFadeOut]);

  return (
    <div className="landing-container">
      <video
        ref={videoRef}
        className="landing-video"
        src="/videos/landing.mp4"
        autoPlay
        muted
        loop={false}
        playsInline
      />
      <div className={`overlay ${isFading ? 'fade-out' : ''}`}></div>
    </div>
  );
}

export default LandingPage;
