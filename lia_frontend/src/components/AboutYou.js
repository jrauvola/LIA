import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './AboutYou.css';

function AboutYou() {
  const [profile, setProfile] = useState({ 
    experience: '', 
    industry: 'Finance', 
    role: '',
    impressive_project: '',
    job_description: ''
  });
  const resumeRef = useRef(null);
  const navigate = useNavigate();
  const [isResumeUploaded, setIsResumeUploaded] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfile({ ...profile, [name]: value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);

    const formData = new FormData();
    const resumeFile = resumeRef.current.files[0];

    if (resumeFile) {
      formData.append('file', resumeFile);
    }
    // Append all profile fields to formData
    Object.entries(profile).forEach(([key, value]) => {
      formData.append(key, value);
    });

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
      navigate('/chatbot');
    } catch (error) {
      console.error('Error uploading resume', error);
      setIsLoading(false);
    }
  };

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

  const LoadingOverlay = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-8 rounded-lg flex flex-col items-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-pink-500 mb-4"></div>
        <p className="text-gray-800">Processing your information...</p>
        <p className="text-gray-600 text-sm mt-2">This may take up to 20 seconds</p>
      </div>
    </div>
  );

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
            name="impressive_project"
            value={profile.impressive_project}
            onChange={handleInputChange}
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
              Include the job description (Recommended)
            </label>
            <input
              type="text"
              name="job_description"
              value={profile.job_description}
              onChange={handleInputChange}
              placeholder="This job entails..."
              className="w-full p-2 border-b border-gray-600 bg-transparent text-gray-400 focus:outline-none"
            />
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={!isResumeUploaded || isLoading}
          className={`fixed bottom-8 right-8 py-3 px-6 rounded-full relative overflow-hidden group
            ${!isResumeUploaded || isLoading
              ? 'bg-gray-400 cursor-not-allowed text-gray-600' 
              : 'bg-white text-black hover:text-white'
            }`}
        >
          <span className={`relative z-10 ${!isResumeUploaded || isLoading ? '' : 'group-hover:text-white'} transition-colors duration-300`}>
            {isLoading
              ? 'Processing...'
              : isResumeUploaded
                ? 'Try a Quick 5 Minute Mock Interview'
                : 'Please Upload Resume First'}
          </span>
          {isResumeUploaded && !isLoading && (
            <div className="absolute bottom-0 left-0 w-full h-0 bg-gradient-to-t from-pink-500 to-pink-400 transition-all duration-500 ease-out group-hover:h-full -z-0
              before:absolute before:content-[''] before:w-full before:h-[10px] before:bottom-full before:left-0 before:bg-[radial-gradient(ellipse_at_center,_rgba(255,192,203,0.35)_0%,_transparent_100%)]
              after:absolute after:content-[''] after:w-full after:h-[10px] after:bottom-full after:left-0 after:bg-[radial-gradient(ellipse_at_center,_rgba(255,192,203,0.35)_0%,_transparent_100%)]">
            </div>
          )}
        </button>
        {isLoading && <LoadingOverlay />}
      </div>
    </div>
  );
}

export default AboutYou;