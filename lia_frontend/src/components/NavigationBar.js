// components/NavigationBar.js
import React from 'react';
import { NavLink } from 'react-router-dom';

function NavigationBar() {
  return (
    <nav className="bg-pink-200 p-4">
      <div className="flex justify-between items-center max-w-6xl mx-auto">
        {/* LIA Logo/Text on the left */}
        <div className="text-gray-800 text-xl font-bold">
          LIA
        </div>
        
        {/* Navigation links moved to the right */}
        <ul className="flex space-x-6">
          <li>
            <NavLink 
              to="/about-you" 
              className={({ isActive }) => 
                isActive ? 'text-gray-800 font-semibold' : 'text-gray-600 hover:text-gray-800'
              }
            >
              About You
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/chatbot" 
              className={({ isActive }) => 
                isActive ? 'text-gray-800 font-semibold' : 'text-gray-600 hover:text-gray-800'
              }
            >
              Improvement Chatbot
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/evaluation" 
              className={({ isActive }) => 
                isActive ? 'text-gray-800 font-semibold' : 'text-gray-600 hover:text-gray-800'
              }
            >
              Evaluation
            </NavLink>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default NavigationBar;

