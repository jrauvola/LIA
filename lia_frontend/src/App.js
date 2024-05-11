// App.js
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AboutYou from './components/AboutYou';
// import Assessment from './components/Assessment';
// import RoadMap from './components/RoadMap';
import Chatbot from './components/Chatbot';
import NavigationBar from './components/NavigationBar';
import { ThemeProvider } from './context/ThemeContext';
import './App.css'; // Import your CSS file for styling

function App() {
  useEffect(() => {
    // Fetch any required data on load or set up initial state
  }, []);

  return (
    <ThemeProvider>
      <Router>
        <NavigationBar />
        <Routes>
          <Route path="/about-you" element={<AboutYou />} />
          {/* <Route path="/assessment" element={<Assessment />} />
          <Route path="/road-map" element={<RoadMap />} /> */}
          <Route path="/chatbot" element={<Chatbot />} />
          {/* ...other routes */}
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
