import React, { useEffect, useState } from 'react';
import './EvaluationPage.css';
import { marked } from 'marked';
import { useLocation, useNavigate } from 'react-router-dom';

const metricDisplayNames = {
  // Text Features
  quantifier_words_pct: "Quantifier Words",
  filler_nonfluency_pct: "Filler Words",
  wpsec: "Words Per Second",
  upsec: "Unique Words Per Second",
  // Audio Features
  avgBand1: 'Average Bandwidth of F1',
  unvoiced_percent: 'Unvoiced Percentage',
  f1STD: 'F1 Standard Deviation',
  f3meanf1: 'F3/F1 Ratio',
  intensityMean: 'Voice Intensity',
  avgDurPause: 'Average Pause Duration',
  // Video Features
  blink_rate: 'Blink Rate',
  average_smile_intensity: 'Smile Intensity',
  average_engagement: 'Engagement Level',
  average_stress: 'Stress Level'
};

const metricDefinitions = {
  // Text Features
  quantifier_words_pct: "The use of quantifier words such as 'all', 'best', 'bunch', 'few', 'ton', 'unique', etc. is a significant predictor of overall interview scores. Quantifier words are used frequently when providing anectodal evidence of your qualifications. More is better, so aim for the advanced zone or higher.",
  filler_nonfluency_pct: "The use of filler words such as 'I mean', 'like', or 'kinda' and nonfluencies such as 'um', 'ahh', or 'er' is a significant predictor of overall interview scores. An excess of fillers and nonfluencies makes your answers difficult to follow and connotes a lack of confidence and familiarity with a given topic. Less is better, so aim for the advanced zone or lower.",
  wpsec: "A high speaking rate causes interviewers to perceive you as confident and competent while allowing you to convey more great things about yourself before the interview ends. More is better, so aim for the advanced zone or higher.",
  upsec: "The ability to use lots of different words quickly shows that you can communicate with precision and have expert domain knowledge. More is better, so aim for the advanced zone or higher.",
  // Audio Features
  avgBand1: "The average bandwidth of formant 1 is a measurement of voice quality and clarity. Lower scores are produced by comfortable speakers who articulate vowel sounds with great clarity. Higher scores are produced by uncomfortable speakers who may be too monotone, tense, or rigid. Aim for the advanced zone or lower.",
  unvoiced_percent: "Pausing is a natural part of speech. However, remaining silent for too great a percentage of the interview can lead to interviewers perceiving that you lack confidence and domain knowledge. Aim for the advanced zone or lower.",
  f1STD: "The standard deviation of formant 1 measures how much your first formant frequency bounces around while you speak. Lower scores indicate confidence, precise articulation of vowel sounds, and professional-sounding speech patterns. Higher scores indicate speech anxiete and unclear articulation of vowel sounds. Aim for the advanced zone or lower.",
  f3meanf1: "The F3/F1 ratio measures the ratio between your third and first formant frequencies. Higher ratios occur when you project your voiec and speak confidently or authoritatively. Lower ratios occur when you speak from the throat, muffle your speech, or fail to project your voice confidently. Aim for the advanced zone or higher.",
  intensityMean: "The intensity mean is a measure of your average loudness/volume. Speaking loudly (but not too loudly) ensures that your words are understood clearly and your interviewer perceives you as confident and assertive. Aim for the advanced zone or higher.",
  avgDurPause: "The average pause duration measures the average length of silent gaps in your speech. If pauses are too long repeatedly, you will likely lose the interviewer's engagement and be perceived as uncertain and ill-prepared. Aim for the advanced zone or lower.",
  // Video Features
  blink_rate: "The blink rate measures your number of blinks per minute. The natural rate for engaged conversation is 10-15 blinks/min. Blinking too much can indicate nervousness or lack of focus. Blinking too little can lead to the interviewer perceiving you as intense and unapproachable. Aim for the middle of the advanced zone.",
  average_smile_intensity: "LiA's face mesh technology measures the intensity of your smile frame-by-frame and produces an average score from the entire mock interview. Each frame is scored between 0% and 100% based on facial muscle engagement. A score of 30-45% demonstrates engagement, approachability, and positivity. Higher scores can indicate nervousness or a lack of sincerity. Lower scores can make you seem unenthusiastic, unengaged, and unfriendly. Aim for the advanced zone.",
  average_engagement: "Engagement is a measurement of how much your face is oriented toward and focused on the camera. A score is measured frame-by-frame and aggregated into the average engagement level of the entire mock interview. A relatively high score of 0.7-0.9 is ideal as it demonstrates good eye contact, active listening, and full engagement. A perfect score of 1.0 may seem unnatural and robotic. A low score results from looking away too often, which implies disinterest or nervousness. Aim for the advanced zone.",
  average_stress: "LiA's face mesh technology studies facial muscle tensions patterns frame-by-frame while you speak. LiA aggregates an average score for your entire mock interview. A relatively low score of 0.1-0.3 demonstrates confidence, composure, and relaxation, which is ideal. Higher scores indicate discomfort and lack of confidence. Aim for the advanced zone or lower."
};

const Tooltip = ({ text, position, onClose }) => {
  if (!position) return null;

  return (
    <div
      className="tooltip"
      style={{
        left: position.x,
        top: position.y
      }}
      onClick={(e) => {
        e.stopPropagation();
        onClose();
      }}
    >
      {text}
    </div>
  );
};

function EvaluationPage() {
  const [interviewData, setInterviewData] = useState(null);
  const [averages, setAverages] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [activeTooltip, setActiveTooltip] = useState(null);
  const [tooltipPosition, setTooltipPosition] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  const location = useLocation();
  const navigate = useNavigate();


  useEffect(() => {
    const handleClickOutside = () => {
      setActiveTooltip(null);
      setTooltipPosition(null);
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  useEffect(() => {
    fetch('http://localhost:80/get_interview_data')
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          console.error('Error fetching interview data:', data.error);
        } else {
          setInterviewData(data);
          const calculatedAverages = calculateAverages(data);
          setAverages(calculatedAverages);
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }, []);

  useEffect(() => {
    fetch('http://localhost:80/scoreboard_breakdown')
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          console.error('Error fetching analysis:', data.error);
        } else {
          setAnalysisResult(data.analysis);
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }, []);

  const MarkupParser = (answer) => {
    return { __html: marked(answer) };
  };

  useEffect(() => {
    setIsVisible(true);
  }, [currentQuestion]);

  const handleTooltipClick = (e, metric) => {
    e.preventDefault();
    e.stopPropagation();

    const rect = e.currentTarget.getBoundingClientRect();

    setActiveTooltip(metric);
    setTooltipPosition({
      x: rect.left,
      y: rect.top - 10  // Changed from rect.bottom to rect.top - 10
    });
  };

  const handleExpertPageNavigation = () => {
    navigate('/expertpage');
  };

  const handleRubricPageNavigation = () => {
    navigate('/rubricpage');
  };

  const calculateAverages = (data) => {
    if (!data) return null;

    const textMetrics = data.text_features.reduce((acc, curr) => {
      acc.quantifier_words_pct += curr.quantifier_words_pct;
      acc.filler_nonfluency_pct += curr.filler_nonfluency_pct;
      acc.wpsec += curr.wpsec;
      acc.upsec += curr.upsec;
      return acc;
    }, {
      quantifier_words_pct: 0,
      filler_nonfluency_pct: 0,
      wpsec: 0,
      upsec: 0
    });

    const count = data.text_features.length;

    return {
      text: {
        quantifier_words_pct: (textMetrics.quantifier_words_pct / count),
        filler_nonfluency_pct: (textMetrics.filler_nonfluency_pct / count),
        wpsec: (textMetrics.wpsec / count),
        upsec: (textMetrics.upsec / count)
      }
    };
  };

  const expertZones = {
    text: {
      quantifier_words_pct: [2.75, 3.42],
      filler_nonfluency_pct: [3.30, 6.48],
      wpsec: [3.11, 3.64],
      upsec: [1.17, 1.38]
    },
    audio: {
      avgBand1: [323.9413, 394.5272],
      unvoiced_percent: [27.39, 36.05],
      f1STD: [262.2278, 300.5224],
      f3meanf1: [4.5702, 4.7801],
      intensityMean: [58.0279, 61.4552],
      avgDurPause: [0.3365, 0.503]
    },
    video: {
      blink_rate: [10, 15],
      average_smile_intensity: [30, 45],
      average_engagement: [0.7, 0.9],
      average_stress: [0.1, 0.3]
    }
  };

  const normalizeValue = (value, feature) => {
    const ranges = {
      // Text features
      quantifier_words_pct: [0, 6],     // 6%
      filler_nonfluency_pct: [0, 10],   // 10%
      wpsec: [0, 5],                    // 5 words per second
      upsec: [0, 4],                    // 4 unique words per second
      // Audio features
      avgBand1: [0, 600],
      unvoiced_percent: [0, 100],
      f1STD: [0, 600],
      f3meanf1: [0, 8],
      intensityMean: [0, 100],
      avgDurPause: [0, 2],
      // Video features
      blink_rate: [0, 30],
      average_smile_intensity: [0, 100],
      average_engagement: [0, 1],
      average_stress: [0, 1]
    };

    const [min, max] = ranges[feature] || [0, 100];
    return Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));
  };

  const getExpertZone = (feature, type) => {
    if (!expertZones[type][feature]) return null;

    const [min, max] = expertZones[type][feature];
    const normalizedMin = normalizeValue(min, feature);
    const normalizedMax = normalizeValue(max, feature);

    let unit = '';
    if (feature.includes('pct') || feature.includes('percent')) unit = '%';
    if (feature.includes('wps')) unit = ' wps';
    if (feature.includes('Band')) unit = ' Hz';
    if (feature.includes('f1STD')) unit = ' Hz';
    if (feature === 'intensityMean') unit = ' dB';
    if (feature.includes('Duration') || feature.includes('Pause')) unit = 's';

    return {
      style: {
        width: `${normalizedMax - normalizedMin}%`,
        left: `${normalizedMin}%`
      },
      range: `Advanced Zone (${min.toFixed(2)} - ${max.toFixed(2)}${unit})`
    };
  };

  const renderTextMetricBar = (metric) => {
    if (!averages?.text[metric]) return null;

    const value = averages.text[metric];
    const displayName = metricDisplayNames[metric];
    const expertZoneData = getExpertZone(metric, 'text');

    return (
      <div className="skill" key={metric}>
        <div
          className="skill-name"
          onClick={(e) => handleTooltipClick(e, metric)}
        >
          {displayName}
        </div>
        <div className="skill-bar-container">
          <div
            className="skill-bar"
            onClick={(e) => handleTooltipClick(e, metric)}
          >
            <div
              className={`skill-per ${isVisible ? 'animate' : ''}`}
              style={{
                '--width': `${normalizeValue(value, metric)}%`,
                backgroundColor: '#ff80ab'
              }}
              data-per={`${value.toFixed(2)}${metric.includes('pct') ? '%' : metric.includes('wps') ? ' wps' : ''}`}
            />
            {expertZoneData && (
              <div
                className="advanced-zone"
                style={expertZoneData.style}
                data-range={expertZoneData.range}
              />
            )}
          </div>
        </div>
        {activeTooltip === metric && (
          <Tooltip
            text={metricDefinitions[metric]}
            position={tooltipPosition}
            onClose={() => setActiveTooltip(null)}
          />
        )}
      </div>
    );
  };

  return (
    !interviewData || !averages ? (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading evaluation data...</p>
      </div>
    ) : (
      <div className="evaluation-container">
        <h1>Social Skills Assessment</h1>

        <div className="question-navigation">
          <div className="navigation-buttons">
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
              View Rubric Assessment
            </button>
          </div>
        </div>

        <div className="skills">
          <h2>Text Features</h2>
          {renderTextMetricBar("quantifier_words_pct")}
          {renderTextMetricBar("filler_nonfluency_pct")}
          {renderTextMetricBar("wpsec")}
          {renderTextMetricBar("upsec")}

          <h2>Audio Features</h2>
          {interviewData.audio_features[currentQuestion] &&
            Object.entries(interviewData.audio_features[currentQuestion])
              .filter(([key]) => key !== 'audio_length' && key !== 'maxDurPause')
              .map(([key, value]) => {
                const expertZoneData = getExpertZone(key, 'audio');
                return (
                  <div className="skill" key={key}>
                    <div
                      className="skill-name"
                      onClick={(e) => handleTooltipClick(e, key)}
                    >
                      {metricDisplayNames[key]}
                    </div>
                    <div className="skill-bar-container">
                      <div
                        className="skill-bar"
                        onClick={(e) => handleTooltipClick(e, key)}
                      >
                        <div
                          className={`skill-per ${isVisible ? 'animate' : ''}`}
                          style={{ '--width': `${normalizeValue(value, key)}%` }}
                          data-per={value.toFixed(2)}
                        />
                        {expertZoneData && (
                          <div
                            className="advanced-zone"
                            style={expertZoneData.style}
                            data-range={expertZoneData.range}
                          />
                        )}
                      </div>
                    </div>
                    {activeTooltip === key && (
                      <Tooltip
                        text={metricDefinitions[key]}
                        position={tooltipPosition}
                        onClose={() => setActiveTooltip(null)}
                      />
                    )}
                  </div>
                );
              })
          }

          <h2>Video Features</h2>
          {interviewData.video_features[currentQuestion] &&
            Object.entries(interviewData.video_features[currentQuestion])
              .filter(([key, value]) =>
                typeof value === 'number' &&
                key !== 'total_frames' &&
                metricDisplayNames[key]
              )
              .map(([key, value]) => {
                const expertZoneData = getExpertZone(key, 'video');
                return (
                  <div className="skill" key={key}>
                    <div
                      className="skill-name"
                      onClick={(e) => handleTooltipClick(e, key)}
                    >
                      {metricDisplayNames[key]}
                    </div>
                    <div className="skill-bar-container">
                      <div
                        className="skill-bar"
                        onClick={(e) => handleTooltipClick(e, key)}
                      >
                        <div
                          className={`skill-per ${isVisible ? 'animate' : ''}`}
                          style={{ '--width': `${normalizeValue(value, key)}%` }}
                          data-per={value.toFixed(2)}
                        />
                        {expertZoneData && (
                          <div
                            className="advanced-zone"
                            style={expertZoneData.style}
                            data-range={expertZoneData.range}
                          />
                        )}
                      </div>
                    </div>
                    {activeTooltip === key && (
                      <Tooltip
                        text={metricDefinitions[key]}
                        position={tooltipPosition}
                        onClose={() => setActiveTooltip(null)}
                      />
                    )}
                  </div>
                );
              })
          }
        </div>

        {/* Add this new section */}
        {analysisResult && (
        <div className="analysis-section">
          <h2>Performance Analysis</h2>
          <div
          className="analysis-content"
          dangerouslySetInnerHTML={MarkupParser(analysisResult)}
          />
          </div>
          )}
      </div>
    )
  );
}

export default EvaluationPage;