import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AboutYou from './components/AboutYou';
import HomePage from './components/HomePage';
import Chatbot from './components/Chatbot';
import EvaluationPage from './components/EvaluationPage';
import NavigationBar from './components/NavigationBar';
import LandingPage from './components/LandingPage';
import { ThemeProvider } from './context/ThemeContext';
import './App.css';

function App() {
  useEffect(() => {
    // Fetch any required data on load or set up initial state
  }, []);

  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/home" element={<><NavigationBar /><HomePage /></>} />
          <Route path="/about-you" element={<><NavigationBar /><AboutYou /></>} />
          <Route path="/chatbot" element={<><NavigationBar /><Chatbot /></>} />
          <Route path="/evaluation" element={<><NavigationBar /><EvaluationPage /></>} />
          {/* Add other routes as needed */}
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;