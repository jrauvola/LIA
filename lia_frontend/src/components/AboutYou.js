import React, { useState } from 'react';
import axios from 'axios';

// Define variables for URLs

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
      const response = await axios.post('https://backend-4e4b4qv3cq-uc.a.run.app/upload_resume', formData, {
        withCredentials: true,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log(response.data);
    } catch (error) {
      console.error('Error uploading resume', error);
    }
  };
  

  return (
    <div className="AboutYou">
      <h1>Welcome to LIA - Large Interview Advisor</h1>
      <input type="file" onChange={handleResumeUpload} />
      <input type="file" onChange={handleResumeUpload} style={{ display: 'none' }} />
      <button onClick={() => document.querySelector('input[type=file]').click()}>
        Upload Resume
      </button>
      

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
      <button onClick={handleSubmit}>Submit About You</button>
    </div>
  );
}

export default AboutYou;
