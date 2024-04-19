// App.js
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
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
        <Switch>
          <Route path="/about-you" component={AboutYou} />
          {/* <Route path="/assessment" component={Assessment} />
          <Route path="/road-map" component={RoadMap} /> */}
          <Route path="/chatbot" component={Chatbot} />
          {/* ...other routes */}
        </Switch>
      </Router>
    </ThemeProvider>
  );
}

export default App;


