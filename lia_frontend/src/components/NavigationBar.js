// components/NavigationBar.js
import React from 'react';
import { NavLink } from 'react-router-dom';

function NavigationBar() {
  return (
    <nav className="navigation-bar">
      <ul>
        <li>
          <NavLink to="/about-you" activeClassName="active">About You</NavLink>
        </li>
        {/* Uncomment when other components are created */}
        {/* <li>
          <NavLink to="/assessment" activeClassName="active">Assessment</NavLink>
        </li>
        <li>
          <NavLink to="/road-map" activeClassName="active">Road Map</NavLink>
        </li>
        */}
        <li>
          <NavLink to="/chatbot" activeClassName="active">Improvement Chatbot</NavLink>
        </li> 
      </ul>
    </nav>
  );
}

export default NavigationBar;
