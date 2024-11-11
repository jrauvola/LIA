// ExpertPage.js
import React, { useState, useEffect } from 'react';
import './ExpertPage.css';

function ExpertPage() {
  const [expertAnswer, setExpertAnswer] = useState('');

  useEffect(() => {
    const fetchExpertAnswer = async () => {
      try {
        const response = await fetch('http://localhost:80/expert_answer', {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        const data = await response.json();
        if (data.expert_answer) {
          setExpertAnswer(data.expert_answer);
        } else {
          setExpertAnswer('No expert answer available at this time.');
        }
      } catch (error) {
        console.error('Error fetching expert answer:', error);
        setExpertAnswer('Failed to load expert answer. Please try again later.');
      }
    };

    fetchExpertAnswer();
  }, []);

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