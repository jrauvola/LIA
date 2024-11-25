// components/NavigationBar.js
import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';

function NavigationBar() {
  const location = useLocation();
  const isAboutYouPage = location.pathname === '/about-you';

  // Style for disabled state
  const disabledStyle = "text-gray-400 cursor-not-allowed pointer-events-none opacity-50";

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
                isAboutYouPage
                  ? disabledStyle
                  : isActive
                    ? 'text-gray-800 font-semibold'
                    : 'text-gray-600 hover:text-gray-800'
              }
              onClick={(e) => isAboutYouPage && e.preventDefault()}
            >
              About You
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/chatbot"
              className={({ isActive }) =>
                isAboutYouPage
                  ? disabledStyle
                  : isActive
                    ? 'text-gray-800 font-semibold'
                    : 'text-gray-600 hover:text-gray-800'
              }
              onClick={(e) => isAboutYouPage && e.preventDefault()}
            >
              Improvement Chatbot
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/evaluation"
              className={({ isActive }) =>
                isAboutYouPage
                  ? disabledStyle
                  : isActive
                    ? 'text-gray-800 font-semibold'
                    : 'text-gray-600 hover:text-gray-800'
              }
              onClick={(e) => isAboutYouPage && e.preventDefault()}
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