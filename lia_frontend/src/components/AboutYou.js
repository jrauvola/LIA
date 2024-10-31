// AboutYou.js
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; // Update this line
import './AboutYou.css';

// // Define variables for URLs
// const GOOGLE_URL = 'https://backend-4e4b4qv3cq-uc.a.run.app';
// const LOCAL_URL = 'http://0.0.0.0:80/';

// // if in development, use the local URL, otherwise use the Google Cloud Run URL
// const API_URL = process.env.NODE_ENV === 'development' ? LOCAL_URL : GOOGLE_URL;
// const UPLOAD_RESUME_URL = `${API_URL}/upload_resume`;

function AboutYou() {
  // const [resume, setResume] = useState(null);
  const [profile, setProfile] = useState({ experience: '', industry: 'Finance', role: '' });
  const resumeRef = useRef(null);
  const navigate = useNavigate(); // Update this line
  const [isResumeUploaded, setIsResumeUploaded] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfile({ ...profile, [name]: value });
  };

const handleSubmit = async (event) => {
  event.preventDefault();
  const formData = new FormData();
  const resumeFile = resumeRef.current.files[0];

  if (resumeFile) {
    formData.append('file', resumeFile);
  }
  formData.append('experience', profile.experience);
  formData.append('industry', profile.industry);
  formData.append('role', profile.role);

  try {
    console.log('Request Config:', {
      method: 'post',
      url: 'http://127.0.0.1/upload_resume',
      data: formData,
      withCredentials: true,
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    const response = await axios.post('http://127.0.0.1/upload_resume', formData, {
      withCredentials: true,
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    console.log('Response Data:', response.data);
  } catch (error) {
    console.error('Error uploading resume', error);
  }

  // Move navigate outside the try-catch block
  navigate('/chatbot'); // Navigate to the chatbot page after the try-catch blocks
};

// Add this function inside the AboutYou component
const handleResumeClick = () => {
  resumeRef.current.click();
};

const handleFileChange = (e) => {
  if (e.target.files[0]) {
    const file = e.target.files[0];
    setUploadedFileName(file.name);
    setIsResumeUploaded(true);
    console.log('File selected:', file.name);
  }
};

return (
  <div className="about-you-container" style={{ backgroundColor: '#000000', minHeight: '100vh' }}>
    <div className="form-container" style={{ 
      width: '80%',
      margin: '0 auto',
      padding: '40px',
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      backgroundColor: 'transparent'
    }}>
      <div className="upload-section mb-8">
        <div 
          onClick={handleResumeClick}
          className={`text-black p-4 rounded-lg text-center cursor-pointer transition-colors ${
            isResumeUploaded 
              ? 'bg-green-300 hover:bg-green-400' 
              : 'bg-pink-200 hover:bg-pink-300'
          }`}
        >
          {isResumeUploaded ? 'Resume Uploaded!' : 'Upload Your Resume'}
        </div>
        <input 
          type="file" 
          ref={resumeRef} 
          className="hidden" 
          id="resume-upload"
          onChange={handleFileChange}
          accept=".pdf,.doc,.docx"
        />
        {/* Show file name if uploaded */}
        {uploadedFileName && (
          <div className="text-gray-400 text-sm mt-2 text-center">
            {uploadedFileName}
          </div>
        )}
      </div>

      <h2 className="text-2xl text-white text-center mb-8">Tell Us About Yourself in A Few Sentences!</h2>

      <div className="mb-6">
        <label className="text-white text-lg mb-2 block">
          Describe your educational and professional experience.
        </label>
        <input
          type="text"
          name="experience"
          value={profile.experience}
          onChange={handleInputChange}
          placeholder="I have designed a rocket..."
          className="w-full p-2 mb-4 border-b border-gray-600 bg-transparent text-gray-400 focus:outline-none"
        />
      </div>

      <div className="mb-6">
        <label className="text-white text-lg mb-2 block">
          What is the most impressive project you have done?
        </label>
        <input
          type="text"
          placeholder="But it blew up..."
          className="w-full p-2 mb-4 border-b border-gray-600 bg-transparent text-gray-400 focus:outline-none"
        />
      </div>

      <div className="mb-6">
        <label className="text-white text-lg mb-2 block">
          Role you are looking to apply for
        </label>
        <input
          type="text"
          name="role"
          value={profile.role}
          onChange={handleInputChange}
          placeholder="So I am looking to apply to ..."
          className="w-full p-2 mb-4 border-b border-gray-600 bg-transparent text-gray-400 focus:outline-none"
        />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="text-white text-lg mb-2 block">
            What is the industry?
          </label>
          <select 
            name="industry" 
            value={profile.industry} 
            onChange={handleInputChange}
            className="w-full p-2 border border-gray-600 rounded bg-transparent text-white"
          >
            <option value="Technology">Technology</option>
            <option value="Finance">Finance</option>
            <option value="Healthcare">Healthcare</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <div>
          <label className="text-white text-lg mb-2 block">
            Company Website Link (Optional)
          </label>
          <input
            type="text"
            placeholder="www.website.com"
            className="w-full p-2 border-b border-gray-600 bg-transparent text-gray-400 focus:outline-none"
          />
        </div>
      </div>

      <button 
        onClick={handleSubmit}
        className="fixed bottom-8 right-8 bg-white text-black py-3 px-6 rounded-full relative overflow-hidden group"
      >
        <span className="relative z-10 group-hover:text-white transition-colors duration-300">
          Try a Quick 5 Minute Mock Interview
        </span>
        <div className="absolute bottom-0 left-0 w-full h-0 bg-gradient-to-t from-pink-500 to-pink-400 transition-all duration-500 ease-out group-hover:h-full -z-0 
          before:absolute before:content-[''] before:w-full before:h-[10px] before:bottom-full before:left-0 before:bg-[radial-gradient(ellipse_at_center,_rgba(255,192,203,0.35)_0%,_transparent_100%)] 
          after:absolute after:content-[''] after:w-full after:h-[10px] after:bottom-full after:left-0 after:bg-[radial-gradient(ellipse_at_center,_rgba(255,192,203,0.35)_0%,_transparent_100%)]"></div>
      </button>
    </div>
  </div>
);
}

export default AboutYou;
