import React, { useEffect, useState } from 'react';
import './EvaluationPage.css';
import { useLocation, useNavigate } from 'react-router-dom';

// Define fixed maximum values for each metric
const maxValues = {
  quantifier_words_pct: 6,    // 6%
  filler_nonfluency_pct: 10,  // 10%
  wpsec: 5,                   // 5 words per second
  upsec: 4,                   // 4 unique words per second
  avgBand1: 600,              // 600 Hz
  unvoiced_percent: 100,      // 100%
  f1STD: 600,                 // 600 Hz
  f3meanf1: 6,                // 6 (ratio)
  intensityMean: 100,         // 100 dB
  avgDurPause: 1,             // 1 second
  average_smile_intensity: 100, // 100%
  average_engagement: 5        // 5%
};

// Advanced zone ranges
const advancedZone = {
  wpsec: { min: 3.1105, max: 3.6397 },
  upsec: { min: 1.1674, max: 1.3761 },
  filler_nonfluency_pct: { min: 3.3033, max: 6.4826 },
  quantifier_words_pct: { min: 2.7538, max: 3.4156 },
  f3meanf1: { min: 4.5702, max: 4.7801 },
  f1STD: { min: 262.2278, max: 300.5224 },
  avgDurPause: { min: 0.3365, max: 0.503 },
  avgBand1: { min: 323.9413, max: 394.5272 },
  intensityMean: { min: 58.0279, max: 61.4552 },
  unvoiced_percent: { min: 27.39, max: 36.05 }
};

const calculateAverages = (data) => {
  if (!data) return null;

  // Text metrics
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

  // Audio metrics
  const audioMetrics = data.audio_features.reduce((acc, curr) => {
    acc.avgBand1 += curr.avgBand1;
    acc.unvoiced_percent += curr.unvoiced_percent;
    acc.f1STD += curr.f1STD;
    acc.f3meanf1 += curr.f3meanf1;
    acc.intensityMean += curr.intensityMean;
    acc.avgDurPause += curr.avgDurPause;
    return acc;
  }, {
    avgBand1: 0,
    unvoiced_percent: 0,
    f1STD: 0,
    f3meanf1: 0,
    intensityMean: 0,
    avgDurPause: 0
  });

  // Video metrics
  const videoMetrics = data.video_features.reduce((acc, curr) => {
    acc.average_smile_intensity += curr.average_smile_intensity;
    acc.average_engagement += curr.average_engagement;
    return acc;
  }, {
    average_smile_intensity: 0,
    average_engagement: 0
  });

  const count = data.text_features.length;

  return {
    text: {
      quantifier_words_pct: (textMetrics.quantifier_words_pct / count),
      filler_nonfluency_pct: (textMetrics.filler_nonfluency_pct / count),
      wpsec: (textMetrics.wpsec / count),
      upsec: (textMetrics.upsec / count)
    },
    audio: {
      avgBand1: (audioMetrics.avgBand1 / count),
      unvoiced_percent: (audioMetrics.unvoiced_percent / count),
      f1STD: (audioMetrics.f1STD / count),
      f3meanf1: (audioMetrics.f3meanf1 / count),
      intensityMean: (audioMetrics.intensityMean / count),
      avgDurPause: (audioMetrics.avgDurPause / count)
    },
    video: {
      average_smile_intensity: (videoMetrics.average_smile_intensity / count),
      average_engagement: (videoMetrics.average_engagement * 100 / count)
    }
  };
};

function EvaluationPage() {
  const [interviewData, setInterviewData] = useState(null);
  const [averages, setAverages] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);

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
    setIsVisible(true);
  }, [currentQuestion]);

  const isInAdvancedZone = (value, range) => {
    if (!range) return false;
    return value >= range.min && value <= range.max;
  };

  const getMetricKey = (name) => {
    const metricMap = {
      "Quantifier Words": "quantifier_words_pct",
      "Filler Words": "filler_nonfluency_pct",
      "Words per Second": "wpsec",
      "Unique Words per Second": "upsec",
      "AvgBand1": "avgBand1",
      "Unvoiced Percent": "unvoiced_percent",
      "Pitch Variation": "f1STD",
      "Formant Ratio": "f3meanf1",
      "Volume": "intensityMean",
      "AvgDurPause": "avgDurPause",
      "Average Smile Intensity": "average_smile_intensity",
      "Average Engagement": "average_engagement"
    };
    return metricMap[name] || name.toLowerCase().replace(/\s+/g, '_');
  };

  const renderSkillBar = (name, value, range, unit = '') => {
    const metricKey = getMetricKey(name);
    const maxValue = maxValues[metricKey];
    const normalizedValue = (value / maxValue) * 100;

    if (!range) {
      return (
        <div className="skill">
          <div className="skill-name">
            {name}
            <span className="skill-min">0{unit}</span>
            <span className="skill-max">{maxValue}{unit}</span>
          </div>
          <div className="skill-bar-container">
            <div className="skill-bar">
              <div
                className={`skill-per ${isVisible ? 'animate' : ''}`}
                style={{
                  '--width': `${normalizedValue}%`,
                  backgroundColor: '#ff80ab'
                }}
                data-per={`${Math.round(value * 100) / 100}${unit}`}
              />
            </div>
          </div>
        </div>
      );
    }

    const normalizedZoneStart = (range.min / maxValue) * 100;
    const normalizedZoneEnd = (range.max / maxValue) * 100;
    const inZone = isInAdvancedZone(value, range);

    return (
      <div className="skill">
        <div className="skill-name">
          {name}
          <span className="skill-range">
            Advanced Zone ({Math.round(range.min * 100) / 100} - {Math.round(range.max * 100) / 100}{unit})
          </span>
          <span className="skill-min">0{unit}</span>
          <span className="skill-max">{maxValue}{unit}</span>
        </div>
        <div className="skill-bar-container">
          <div className="skill-bar">
            <div
              className={`skill-per ${isVisible ? 'animate' : ''}`}
              style={{
                '--width': `${normalizedValue}%`,
                backgroundColor: inZone ? '#4A90E2' : '#ff80ab'
              }}
              data-per={`${Math.round(value * 100) / 100}${unit}`}
            />
            <div
              className="advanced-zone-overlay"
              style={{
                left: `${normalizedZoneStart}%`,
                width: `${normalizedZoneEnd - normalizedZoneStart}%`
              }}
            >
              <span className="zone-label">Advanced Zone</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (!averages) {
    return <div>Loading evaluation data...</div>;
  }

  return (
    <div className="evaluation-container">
      <h1>Social Skills Analysis</h1>

      <div className="metrics-section">
        <h2>Text Metrics</h2>
        {renderSkillBar("Quantifier Words", averages.text.quantifier_words_pct, advancedZone.quantifier_words_pct, '%')}
        {renderSkillBar("Filler Words", averages.text.filler_nonfluency_pct, advancedZone.filler_nonfluency_pct, '%')}
        {renderSkillBar("Words per Second", averages.text.wpsec, advancedZone.wpsec, ' wps')}
        {renderSkillBar("Unique Words per Second", averages.text.upsec, advancedZone.upsec, ' wps')}

        <h2>Audio Metrics</h2>
        {renderSkillBar("AvgBand1", averages.audio.avgBand1, advancedZone.avgBand1, ' Hz')}
        {renderSkillBar("Unvoiced Percent", averages.audio.unvoiced_percent, advancedZone.unvoiced_percent, '%')}
        {renderSkillBar("Pitch Variation", averages.audio.f1STD, advancedZone.f1STD, ' Hz')}
        {renderSkillBar("Formant Ratio", averages.audio.f3meanf1, advancedZone.f3meanf1)}
        {renderSkillBar("Volume", averages.audio.intensityMean, advancedZone.intensityMean, ' dB')}
        {renderSkillBar("AvgDurPause", averages.audio.avgDurPause, advancedZone.avgDurPause, 's')}

        <h2>Video Metrics</h2>
        {renderSkillBar("Average Smile Intensity", averages.video.average_smile_intensity, null, '%')}
        {renderSkillBar("Average Engagement", averages.video.average_engagement, null, '%')}
      </div>

      <div className="navigation-buttons">
        <button className="view-button expert-button">
          View Expert Answers
        </button>
        <button className="view-button rubric-button">
          View Rubric
        </button>
      </div>
    </div>
  );
}

export default EvaluationPage;