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

return (
  <div className="about-you-container">
    <div className="form-container">
      <h1 className="text-3xl font-bold mb-6">Welcome to LIA - Large Interview Advisor</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" ref={resumeRef} className="mb-4" />
        <input
          type="text"
          placeholder="Describe your educational and professional experience."
          name="experience"
          value={profile.experience}
          onChange={handleInputChange}
          className="w-full p-2 mb-4 border rounded"
        />
        <select 
          name="industry" 
          value={profile.industry} 
          onChange={handleInputChange}
          className="w-full p-2 mb-4 border rounded"
        >
          <option value="Technology">Technology</option>
          <option value="Finance">Finance</option>
          <option value="Healthcare">Healthcare</option>
          <option value="Other">Other</option>
        </select>
        <input
          type="text"
          placeholder="Role you are looking to apply for:"
          name="role"
          value={profile.role}
          onChange={handleInputChange}
          className="w-full p-2 mb-4 border rounded"
        />
        <button 
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700"
        >
          Submit About You
        </button>
      </form>
    </div>
    <div className="image-container">
      <img src="/AboutMeDesign.png" alt="Interview" />
    </div>
  </div>
);
}

export default AboutYou;
