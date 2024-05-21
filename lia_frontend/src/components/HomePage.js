// HomePage.js

import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';  // Make sure to create and import this CSS file

function HomePage() {
  const navigate = useNavigate();

  const handleEnter = () => {
    navigate('/about-you');
  };

  return (
    <div className="homepage-container">
      <img
        className="background-video"
        src="/images/background.jpeg"
        alt="Background"
      />
      <div className="overlay-content">
        <div className="flex flex-col justify-center flex-1 pl-16">
          <h1 className="text-8xl font-bold mb-4">
            <span className="highlight">L</span>arge <br />
            <span className="highlight">I</span>nterview <br />
            <span className="highlight">A</span>dvisor
          </h1>
          <button
            onClick={handleEnter}
            className="px-6 py-3 mt-8 text-lg bg-blue-500 text-white rounded hover:bg-blue-700"
          >
            Enter
          </button>
        </div>
      </div>
    </div>
  );
}

export default HomePage;


