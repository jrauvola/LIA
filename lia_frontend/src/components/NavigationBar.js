// components/NavigationBar.js
import React from 'react';
import { NavLink } from 'react-router-dom';

function NavigationBar() {
  return (
    <nav className="bg-gray-800 p-4">
      <ul className="flex space-x-4">
        <li>
          <NavLink 
            to="/about-you" 
            className={({ isActive }) => 
              isActive ? 'text-white' : 'text-gray-300 hover:text-white'
            }
          >
            About You
          </NavLink>
        </li>
        <li>
          <NavLink 
            to="/chatbot" 
            className={({ isActive }) => 
              isActive ? 'text-white' : 'text-gray-300 hover:text-white'
            }
          >
            Improvement Chatbot
          </NavLink>
        </li>
        <li>
          <NavLink 
            to="/evaluation" 
            className={({ isActive }) => 
              isActive ? 'text-white' : 'text-gray-300 hover:text-white'
            }
          >
            Evaluation
          </NavLink>
        </li>
        {/* Add more links as needed */}
      </ul>
    </nav>
  );
}

export default NavigationBar;

