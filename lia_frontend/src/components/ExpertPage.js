// ExpertPage.js
import React, { useState, useEffect } from 'react';
import './ExpertPage.css';

function ExpertPage() {
  const [expertAnswer, setExpertAnswer] = useState('');

  useEffect(() => {
    // Function to fetch data from Gemini API
    const fetchExpertAnswer = async () => {
      try {
        // Replace with your actual API endpoint and configuration
        const response = await fetch('YOUR_GEMINI_API_ENDPOINT', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            // Add any necessary API keys or authentication headers
          }
        });
        
        const data = await response.json();
        setExpertAnswer(data.answer); // Adjust based on actual API response structure
      } catch (error) {
        console.error('Error fetching expert answer:', error);
        setExpertAnswer('Failed to load expert answer. Please try again later.');
      }
    };

    fetchExpertAnswer();
  }, []); // Empty dependency array means this runs once when component mounts

  return (
    <div className="expert-container">
      <div className="expert-textbox">
        <h2>Expert Example Answer</h2>
        <p>{expertAnswer}</p>
      </div>
    </div>
  );
}

export default ExpertPage;
