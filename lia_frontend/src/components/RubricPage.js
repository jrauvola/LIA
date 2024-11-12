import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RubricPage.css';

const RubricPage = () => {
  const [rubricData, setRubricData] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch rubric data when component mounts
  useEffect(() => {
    const fetchRubricData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1/rubric_score');
        // Extract the first (and only) evaluation object from the dict
        const evaluationData = response.data[0];
        setRubricData(evaluationData);
        // Set the first category as default selected
        const firstCategory = Object.keys(evaluationData)[0];
        setSelectedCategory(firstCategory);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching rubric data:', err);
        setError('Failed to load rubric data. Please try again later.');
        setLoading(false);
      }
    };

    fetchRubricData();
  }, []);

  const handleCategoryClick = (category) => {
    setSelectedCategory(category);
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
  );
};

export default RubricPage;
