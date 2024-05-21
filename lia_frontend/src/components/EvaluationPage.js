//EvaluationPage.js
import React from 'react';
import './EvaluationPage.css';

const evaluationData = {
  "Overall": [
    {
      "score": "4.4",
      "feedback": "The interviewee is a strong candidate, but some of their answers lack detail and clarity. They also seem to get flustered at times, particularly when describing their weaknesses."
    }
  ],
  "RecommendHiring": [
    {
      "score": "4.2",
      "feedback": "The interviewee's qualifications seem good, but their communication skills need improvement."
    }
  ],
  "Colleague": [
    {
      "score": "4.3",
      "feedback": "The interviewee demonstrates good teamwork skills, but their communication could be more concise and clear."
    }
  ],
  "Engaged": [
    {
      "score": "5.1",
      "feedback": "The interviewee seems genuinely interested in the position and engaged in the conversation."
    }
  ],
  "Excited": [
    {
      "score": "4.6",
      "feedback": "The interviewee expresses enthusiasm for the role, but their excitement could be more clearly conveyed."
    }
  ],
  "NoFillers": [
    {
      "score": "3.6",
      "feedback": "The interviewee uses a fair amount of filler words and phrases, which can detract from their professionalism."
    }
  ],
  "Friendly": [
    {
      "score": "5.0",
      "feedback": "The interviewee comes across as friendly and approachable."
    }
  ],
  "Paused": [
    {
      "score": "4.8",
      "feedback": "The interviewee pauses frequently, which can make their answers seem hesitant."
    }
  ],
  "StructuredAnswers": [
    {
      "score": "4.5",
      "feedback": "The interviewee's answers are generally well-structured, but they could be more concise and focused."
    }
  ],
  "Calm": [
    {
      "score": "4.8",
      "feedback": "The interviewee appears calm and collected, but their occasional hesitations suggest some nervousness."
    }
  ],
  "Focused": [
    {
      "score": "4.9",
      "feedback": "The interviewee seems focused on the conversation, but their answers could be more specific and detailed."
    }
  ],
  "Authentic": [
    {
      "score": "5.2",
      "feedback": "The interviewee comes across as authentic and genuine."
    }
  ],
  "NotAwkward": [
    {
      "score": "5.0",
      "feedback": "The interviewee is comfortable and engaging, with no awkward moments."
    }
  ],
  "Total": [
    {
      "score": "82.5",
      "feedback": "The interviewee has potential, but needs to work on their communication skills to be a truly strong candidate."
    }
  ]
};

function EvaluationPage() {
  return (
    <div className="evaluation-container">
      <h1>Interview Evaluation</h1>
      {Object.keys(evaluationData).map((category) => (
        <div key={category} className="evaluation-category">
          <h2>{category}</h2>
          <p><strong>Score:</strong> {evaluationData[category][0].score}</p>
          <p><strong>Feedback:</strong> {evaluationData[category][0].feedback}</p>
        </div>
      ))}
    </div>
  );
}

export default EvaluationPage;