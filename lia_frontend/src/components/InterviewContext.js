import React, { createContext, useContext, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';

const InterviewContext = createContext();

export function InterviewProvider({ children }) {
   // States that need to persist
   const [conversation, setConversation] = useState([]);
   const [attemptCount, setAttemptCount] = useState(0);
   const [showFeedbackButton, setShowFeedbackButton] = useState(false);
   const [questionCount, setQuestionCount] = useState(0);

   // Function to add a message to conversation
   const addMessage = (role, message) => {
       setConversation(prev => [...prev, { id: uuidv4(), role, message }]);
   };

   // Function to increment attempt count
   const incrementAttemptCount = () => {
       const newCount = attemptCount + 1;
       setAttemptCount(newCount);
       if (newCount > 4) {
           setShowFeedbackButton(true);
       }
   };

   // Values to share across components
   const value = {
       conversation,
       setConversation,
       attemptCount,
       setAttemptCount,
       showFeedbackButton,
       setShowFeedbackButton,
       questionCount,
       setQuestionCount,
       addMessage,
       incrementAttemptCount
   };

   return (
       <InterviewContext.Provider value={value}>
           {children}
       </InterviewContext.Provider>
   );
}

// Custom hook to use the interview context
export function useInterview() {
   const context = useContext(InterviewContext);
   if (context === undefined) {
       throw new Error('useInterview must be used within an InterviewProvider');
   }
   return context;
}