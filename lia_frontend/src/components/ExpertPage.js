import React, { useState, useEffect } from 'react';
import { marked } from 'marked';
import './ExpertPage.css';
import { useLocation, useNavigate } from 'react-router-dom';

function ExpertPage() {
  const [expertData, setExpertData] = useState({
    question: '',
    expert_answer: '',
    current_question: 0,
    total_questions: 0
  });
  const [error, setError] = useState(null);

  const location = useLocation();
  const navigate = useNavigate();

  const handleEvaluationPageNavigation = () => {
    navigate('/evaluation');
  };

  const handleRubricPageNavigation = () => {
    navigate('/rubricpage');
  };

  const fetchExpertAnswer = async (questionNum) => {
    try {
      const response = await fetch(`http://localhost:80/expert_answer?question_num=${questionNum}`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch expert answer');
      }

      const data = await response.json();
      setExpertData(data);
      setError(null);
    } catch (error) {
      console.error('Error fetching expert answer:', error);
      setError('Failed to load expert answer. Please try again later.');
    }
  };

  useEffect(() => {
    fetchExpertAnswer(0); // Start with first question
  }, []);

  const handleNext = () => {
    if (expertData.current_question < expertData.total_questions - 1) {
      fetchExpertAnswer(expertData.current_question + 1);
    }
  };

  const handlePrevious = () => {
    if (expertData.current_question > 0) {
      fetchExpertAnswer(expertData.current_question - 1);
    }
  };

  const renderExpertAnswer = (answer) => {
    return { __html: marked(answer) };
  };

  return (

    <div className="expert-container">

      <div className="question-navigation">
        <div className="navigation-buttons">
          <button
            onClick={handleEvaluationPageNavigation}
            className="view-button expert-button"
          >
            View Social Skills Assessment
          </button>
          <button
            onClick={handleRubricPageNavigation}
            className="view-button rubric-button"
          >
            View Rubric Assessment
          </button>
        </div>
      </div>

      <div className="expert-textbox">
        <h2>LIA's Expert Answer</h2>
        {error ? (
          <p className="error-message">{error}</p>
        ) : (
          <>
            <div className="question-section">
              <h3>Question {expertData.current_question + 1}:</h3>
              <p>{expertData.question}</p>
            </div>
            <div className="answer-section">
              <h3>Expert Answer:</h3>
              <div
                  className="expert-answer"
                  dangerouslySetInnerHTML={renderExpertAnswer(expertData.expert_answer)}
                  
                  
              />

            </div>
            <div className="navigation-buttons">
              <button
                  onClick={handlePrevious}
                  disabled={expertData.current_question === 0}
                className="nav-button"
              >
                Previous
              </button>
              <span className="question-counter">
                {expertData.current_question + 1} of {expertData.total_questions}
              </span>
              <button
                onClick={handleNext}
                disabled={expertData.current_question === expertData.total_questions - 1}
                className="nav-button"
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default ExpertPage;