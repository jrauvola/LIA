import React from 'react';

const PerformanceAnalysis = ({ analysisData }) => {
  if (!analysisData) return null;

  const renderFeedbackSection = (title, feedbackData) => (
    <div className="feedback-section">
      <h3>{title}</h3>
      <div className="feedback-grid">
        <div className="feedback-box strength">
          <h4>Strength</h4>
          <p>{feedbackData.strength}</p>
        </div>
        <div className="feedback-box weakness">
          <h4>Area for Improvement</h4>
          <p>{feedbackData.weakness}</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="performance-analysis">
      <div className="overall-section">
        <h3>Overall Assessment</h3>
        <p>{analysisData.overall_feedback}</p>
      </div>

      {renderFeedbackSection("Text Features", analysisData.text_feedback)}
      {renderFeedbackSection("Audio Features", analysisData.audio_feedback)}
      {renderFeedbackSection("Video Features", analysisData.video_feedback)}
    </div>
  );
};

export default PerformanceAnalysis;