import React, { useEffect, useState } from 'react';
import './EvaluationPage.css';
import { useLocation, useNavigate } from 'react-router-dom';

function EvaluationPage() {
  const [interviewData, setInterviewData] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const location = useLocation();
  const navigate = useNavigate();

  // useEffect(() => {
  //   // Fetch interview data immediately when navigating to this page
  //   fetch('http://localhost:5000/get_interview_data')
  //     .then(response => response.json())
  //     .then(data => {
  //       if (data.error) {
  //         console.error('Error fetching interview data:', data.error);

  //       } else {
  //         setInterviewData(data);
  //       }
  //     })
  //     .catch(error => {
  //       console.error('Error:', error);
  //     });
  // }, []); // Empty dependency array means this runs once when component mounts

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

  return (
    interviewData ? (
      <div>Loading evaluation data...</div>
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
          {renderSkillBar("% Smile", metrics.smilePercentage, expertMetrics.smilePercentage)}
          {renderSkillBar("Speaking Rate", metrics.speakingRate, expertMetrics.speakingRate)}
          {renderSkillBar("% Unvoiced", metrics.unvoicedPercentage, expertMetrics.unvoicedPercentage)}
          {renderSkillBar("Expressiveness", metrics.expressiveness, expertMetrics.expressiveness)}
          {renderSkillBar("Monotone", metrics.monotone, expertMetrics.monotone)}
          {renderSkillBar("Positive Emotion Words", metrics.positiveEmotionWords, expertMetrics.positiveEmotionWords)}
          {renderSkillBar("Quantifier Words", metrics.quantifierWords, expertMetrics.quantifierWords)}
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