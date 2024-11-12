import React, { useEffect, useState } from 'react';
import './EvaluationPage.css';
import { useLocation, useNavigate } from 'react-router-dom';

function EvaluationPage() {
  const [interviewData, setInterviewData] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:80/get_interview_data')
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          console.error('Error fetching interview data:', data.error);
        } else {
          setInterviewData(data);
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }, []);

  useEffect(() => {
    setIsVisible(true);
  }, [currentQuestion]);

  const handleExpertPageNavigation = () => {
    navigate('/expertpage');
  };

  const handleRubricPageNavigation = () => {
    navigate('/rubricpage');
  };

  // Placeholder metrics instead of real data
  const metrics = {
    smilePercentage: 12,
    speakingRate: 65,
    unvoicedPercentage: 15,
    expressiveness: 75,
    monotone: 45,
    positiveEmotionWords: 35,
    quantifierWords: 25
  };

  // Expert reference values
  const expertMetrics = {
    smilePercentage: 15,
    speakingRate: 70,
    unvoicedPercentage: 20,
    expressiveness: 80,
    monotone: 30,
    positiveEmotionWords: 60,
    quantifierWords: 20
  };

  // Assessment text
  const assessmentText = {
    good: [
      {
        title: "% Smile",
        text: "You shined your bright smile within the recommended range of 10-15% of the interview. You are killin' it. Smile on."
      },
      {
        title: "% Unvoiced",
        text: "You avoided awkward pauses and maintained the interviewer's attention. Now that's what I call rizz."
      }
    ],
    bad: [
      {
        title: "Positive Emotion Words",
        text: "You fell short of the recommended usage of positive emotion words (excited, hopeful, love, etc). Express your passion more next time."
      },
      {
        title: "Monotone",
        text: "My audio analyzer picked up that your voice stayed in the same emotional range too consistently, which means you lacked expressiveness. Try to dial up your emotions next time."
      }
    ]
  };

  const renderSkillBar = (name, value, expertValue) => (
    <div className="skill">
      <div className="skill-name">{name}</div>
      <div className="skill-bar-container">
        <div className="skill-bar">
          <div
            className={`skill-per ${isVisible ? 'animate' : ''}`}
            style={{ '--width': `${value}%` }}
            data-per={`${Math.round(value)}%`}
          />
        </div>
        <div className="skill-bar expert">
          <div
            className="skill-per"
            style={{ width: `${expertValue}%` }}
            data-per="Expert"
          />
        </div>
      </div>
    </div>
  );

  const totalQuestions = Object.keys(interviewData?.interview_dict || {}).length;

  // Expert zones (hardcoded)
  const expertZones = {
    audio: {
      avgBand1: [323.9413, 394.5272],
      unvoiced_percent: [27.39, 36.05], // Converted from 0.2739, 0.3605
      f1STD: [262.2278, 300.5224],
      f3meanf1: [4.5702, 4.7801],
      intensityMean: [58.0279, 61.4552],
      avgDurPause: [0.3365, 0.503],
      maxDurPause: [0.4, 0.6] // Made up range
    },
    video: {
      blink_rate: [10, 15],
      average_smile_intensity: [30, 45],
      average_engagement: [0.7, 0.9],
      average_stress: [0.1, 0.3]
    }
  };

  // Normalize value to 0-100 scale based on feature type
  const normalizeValue = (value, feature) => {
    const ranges = {
      avgBand1: [0, 600],
      unvoiced_percent: [0, 100],
      f1STD: [0, 600],
      f3meanf1: [0, 8],
      intensityMean: [0, 100],
      avgDurPause: [0, 2],
      maxDurPause: [0, 2],
      blink_rate: [0, 30],
      average_smile_intensity: [0, 100],
      average_engagement: [0, 1],
      average_stress: [0, 1]
    };

    const [min, max] = ranges[feature] || [0, 100];
    return Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));
  };

  // Calculate expert zone position and width
  const getExpertZone = (feature, type) => {
    if (!expertZones[type][feature]) return null;
    
    const [min, max] = expertZones[type][feature];
    const normalizedMin = normalizeValue(min, feature);
    const normalizedMax = normalizeValue(max, feature);
    
    return {
      width: `${normalizedMax - normalizedMin}%`,
      left: `${normalizedMin}%`
    };
  };

  const getDisplayName = (key) => {
    const displayNames = {
      avgBand1: 'Average Bandwidth',
      unvoiced_percent: 'Unvoiced Percentage',
      f1STD: 'F1 Standard Deviation',
      f3meanf1: 'F3/F1 Ratio',
      intensityMean: 'Voice Intensity',
      avgDurPause: 'Average Pause Duration',
      maxDurPause: 'Maximum Pause Duration',
      blink_rate: 'Blink Rate',
      average_smile_intensity: 'Smile Intensity',
      average_engagement: 'Engagement Level',
      average_stress: 'Stress Level'
    };
    return displayNames[key] || key;
  };

  return (
    !interviewData ? (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading evaluation data...</p>
      </div>
    ) : (
      <div className="evaluation-container">
        <h1>Social Skills Assessment</h1>

        <div className="question-navigation">
          <span>Question {currentQuestion + 1} of {1}</span>
          <div className="navigation-buttons">
            <button
              onClick={() => setCurrentQuestion(prev => Math.max(0, prev - 1))}
              disabled={currentQuestion === 0}
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentQuestion(prev => Math.min(totalQuestions - 1, prev + 1))}
              disabled={currentQuestion === totalQuestions - 1}
            >
              Next
            </button>
            <button
              onClick={handleExpertPageNavigation}
              className="view-button expert-button"
            >
              View Expert Answers
            </button>
            <button
              onClick={handleRubricPageNavigation}
              className="view-button rubric-button"
            >
              View Rubric
            </button>
          </div>
        </div>

        <div className="skills">
          <h2>Audio Features</h2>
          {interviewData.audio_features[currentQuestion] && 
            Object.entries(interviewData.audio_features[currentQuestion])
              .filter(([key]) => key !== 'audio_length')
              .map(([key, value]) => (
                <div className="skill" key={key}>
                  <div className="skill-name">{getDisplayName(key)}</div>
                  <div className="skill-bar-container">
                    <div className="skill-bar">
                      <div
                        className={`skill-per ${isVisible ? 'animate' : ''}`}
                        style={{ '--width': `${normalizeValue(value, key)}%` }}
                        data-per={value.toFixed(2)}
                      />
                      {getExpertZone(key, 'audio') && (
                        <div 
                          className="expert-zone"
                          style={getExpertZone(key, 'audio')}
                        />
                      )}
                    </div>
                  </div>
                </div>
              ))
          }

          <h2>Video Features</h2>
          {interviewData.video_features[currentQuestion] && 
            Object.entries(interviewData.video_features[currentQuestion])
              .filter(([key, value]) => typeof value === 'number') // Only show numeric values
              .map(([key, value]) => (
                <div className="skill" key={key}>
                  <div className="skill-name">{key}</div>
                  <div className="skill-bar-container">
                    <div className="skill-bar">
                      <div
                        className={`skill-per ${isVisible ? 'animate' : ''}`}
                        style={{ '--width': `${Math.min(value * 100, 100)}%` }}
                        data-per={`${Math.round(value * 100) / 100}`}
                      />
                    </div>
                  </div>
                </div>
              ))
          }
        </div>

        <div className="assessment-section">
          <div className="good-feedback">
            <h2>The Good:</h2>
            {assessmentText.good.map((item, index) => (
              <div key={index} className="feedback-item">
                <strong>{item.title}</strong> - {item.text}
              </div>
            ))}
          </div>

          <div className="bad-feedback">
            <h2>The Bad:</h2>
            {assessmentText.bad.map((item, index) => (
              <div key={index} className="feedback-item">
                <strong>{item.title}</strong> - {item.text}
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  );
}

export default EvaluationPage;