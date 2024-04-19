import React, { useState } from 'react';
import axios from 'axios';

function AboutYou() {
  const [resume, setResume] = useState(null);
  const [profile, setProfile] = useState({
    education: '',
    impressiveProject: '',
    improvement: '',
    industry: 'Technology',
    companyWebsite: ''
  });

  const handleResumeUpload = (event) => {
    setResume(event.target.files[0]);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfile({ ...profile, [name]: value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('file', resume);
    try {
      await axios.post('/upload_resume', formData);
      await axios.post('/submit_about', profile);
      // Handle success, clear form, etc.
    } catch (error) {
      console.error('Error submitting form', error);
      // Handle errors
    }
  };
  

  return (
    <div className="AboutYou">
      <h1>Welcome to LIA - Large Interview Advisor</h1>
      <input type="file" onChange={handleResumeUpload} />
      <button onClick={() => document.querySelector('input[type=file]').click()}>Submit Resume</button>
      <button onClick={handleSubmit}>Assess Resume</button>

      <input 
        type="text" 
        placeholder="Describe your educational and professional experience."
        name="education"
        value={profile.education}
        onChange={handleInputChange}
      />

      {/* ...other input fields similar to the one above... */}

      <select 
        name="industry" 
        value={profile.industry}
        onChange={handleInputChange}
      >
        <option value="Technology">Technology</option>
        <option value="Finance">Finance</option>
        <option value="Healthcare">Healthcare</option>
        <option value="Other">Other</option>
      </select>

      <input 
        type="text" 
        placeholder="Company Website:"
        name="companyWebsite"
        value={profile.companyWebsite}
        onChange={handleInputChange}
      />
    </div>
  );
}

export default AboutYou;