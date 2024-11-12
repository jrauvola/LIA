import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RubricPage.css';

const RubricPage = () => {
  const [rubricData, setRubricData] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch rubric data when component mounts or question changes
  useEffect(() => {
    const fetchRubricData = async () => {
      try {
        const response = await axios.get(`http://localhost:80/rubric_score?question_num=${currentQuestion}`);
        setRubricData(response.data.rubric_categories);
        setTotalQuestions(response.data.total_questions);

        // Set the first category as default selected if not already selected
        if (!selectedCategory && response.data.rubric_categories) {
          const firstCategory = Object.keys(response.data.rubric_categories)[0];
          setSelectedCategory(firstCategory);
        }
        setLoading(false);
      } catch (err) {
        console.error('Error fetching rubric data:', err);
        setError('Failed to load rubric data. Please try again later.');
        setLoading(false);
      }
    };

    fetchRubricData();
  }, [currentQuestion]); // Re-fetch when question changes

  const handleCategoryClick = (category) => {
    setSelectedCategory(category);
  };

  const handleNextQuestion = () => {
    if (currentQuestion < totalQuestions - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  if (loading) {
    return <div className="rubric-container">Loading rubric data...</div>;
  }

  if (error) {
    return <div className="rubric-container">{error}</div>;
  }

  if (!rubricData) {
    return <div className="rubric-container">No rubric data available.</div>;
  }

  return (
    <div className="rubric-container">
      <div className="question-navigation">
        <button
          className="nav-button"
          onClick={handlePreviousQuestion}
          disabled={currentQuestion === 0}
        >
          Previous Question
        </button>
        <span className="question-indicator">
          Question {currentQuestion + 1} of {totalQuestions}
        </span>
        <button
          className="nav-button"
          onClick={handleNextQuestion}
          disabled={currentQuestion === totalQuestions - 1}
        >
          Next Question
        </button>
      </div>

      <div className="rubric-content">
        <div className="rubric-categories">
          <h2>Evaluation Rubric</h2>
          {Object.entries(rubricData).map(([category, data]) => (
            <div
              key={category}
              className={`category-item ${selectedCategory === category ? 'active' : ''}`}
              onClick={() => handleCategoryClick(category)}
            >
              <span className="category-name">{category}</span>
              <span className="category-score">{data.Score}/10</span>
            </div>
          ))}
        </div>

        <div className="justification-panel">
          <h2>Justification</h2>
          <div className="justification-content">
            {selectedCategory && (
              <>
                <h3 className="justification-title">{selectedCategory}</h3>
                <p className="justification-text">
                  {rubricData[selectedCategory].Justification || 'No justification provided.'}
                </p>
                <div className="score-display">
                  Score: {rubricData[selectedCategory].Score}/10
                </div>
              </>
            )}
            {!selectedCategory && (
              <p>Select a category to view its justification.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RubricPage;