<h1 align="center">LIA: Large Interview Assistant

AI-Powered Interview Preparation Tool </h1>


<div align="center">
    <img src="https://github.com/jrauvola/LIA/blob/master/logo.png" alt="Description" width="500" height="300">
</div>

LiA (Large Interview Assistant) is an AI-powered tool that helps users prepare for job interviews through interactive practice sessions and real-time feedback. It tailors questions to various tech fields, like data science, and provides personalized guidance, helping users improve their responses and gain confidence for real-world interviews.

# **📑 Table of Contents**
1. [Project Motivation](#Project-Motivation)
2. [Overview of LiA](#Overview-of-LiA)
3. [Project](#project)
   * [LiA's Brain: Our LLM Agents](#lias-brain-our-llm-agents)
     * [Question Generation Agent](#question-generation-agent)
     * [Expert Agent](#expert-agent)
     * [Evaluation Agent](#evaluation-agent)
   * [LiA's Real Time Information: Tracking Your Confidence in Real-Time](#liAs-real-time-information-tracking-your-confidence-in-real-time)
   * [LiA's Interface: Your Interview Playground](#lias-interface-your-interview-playground)
   * [LiA's Toolkit: The Technology Behind the Magic](#lias-toolkit-the-technology-behind-the-magic)
7. [Future Works](#Future-Works)
8. [Tools Utilized](#Tools-Utilized)
9. [About Us](#About-Us)

# **💡Project Motivation**

Meet **Khushi**, a data science graduate excited to start her career but feeling overwhelmed by the challenges of breaking into the competitive job market. Like many new graduates, Khushi struggles with interview anxiety. The moment she sits in front of an interviewer, her mind goes blank. She finds it especially hard to confidently tackle technical questions or articulate her achievements.

Khushi’s journey into data science is still in its early stages—she doesn’t have much experience yet and often feels unsure about how to prepare for interviews effectively. To make things harder, Khushi sometimes feels she's behind her peers. Many of them seem to have stronger technical skills or more impressive projects, leaving her with a sense of playing catch-up.

**That’s where LiA steps in.**

LiA leverages the power of AI to provide an interactive interview practice environment. Whether you're preparing for behavioral interviews, technical questions, or data science case studies, LiA is here to simulate real interview scenarios, giving you the confidence to succeed.

**Key Features:**
- **Interactive Q&A Sessions**: Practice answering behavioral, technical, and domain-specific questions.
- **Real-Time Feedback**: Receive instant feedback on the quality of your answers, including tips for improvement.
- **Tailored Practice**: Customize your sessions based on the job you're applying for.
- **Progress Tracking**: Track your performance over time and focus on areas that need improvement.

# **📣Overview of LiA**
![alt text](https://github.com/jrauvola/LIA/blob/master/workflow.png)

# **🎢Project** 
## **🧠LiA's Brain: Our LLM Agents**
At the core of LiA lies a sophisticated network of Language Model (LLM) agents, each designed to enhance your interview preparation experience. These agents leverage advanced AI technologies to provide personalized support, guidance, and feedback tailored to your unique needs.

Together, these agents form a comprehensive support system, empowering Khushi to tackle interviews with confidence and skill.

### **💬Question Generation Agent**
This agent takes key information about the candidate’s prior experience, project background, and details of the role they are preparing for—such as a **Data Scientist position in the Gaming Industry**. By leveraging this contextual data, the agent formulates highly relevant and customized interview questions that align with both the candidate’s expertise and the target industry.

**Input Gathering**: The agent collects input on the candidate’s past roles, project details, target industry, and role requirements to build a comprehensive profile.

**LLM Integration**: This profile is then fed into Gemini by LiA, and is optimized through prompt engineering. By crafting precise prompts, Gemini is guided to generate questions that reflect the nuances of the candidate’s background in relation to their future role.

**Industry & Experience-Personalized Questions**: The model generates a set of personalized interview questions, drawing on industry trends, specific technical skills, and behavioral competencies tailored to the Data Scientist in Gaming scenario (or similar positions).

### **👩‍🔬Expert Agent**
The **Expert Agent** is your personal interview coach within LiA, specializing in generating high-quality, customized example answers for interview questions. Designed to help users understand and convey their skills effectively, the Expert Agent tailors its responses using key details from both the user’s resume and the target job description. This customization allows users to see how to leverage their unique experiences, skills, and qualifications to meet job-specific expectations.

**Version Testing and Enhancements**
To ensure the best performance, we developed and tested three different versions of the Expert Agent:

- **RAG (Retrieval-Augmented Generation)**: The RAG model combines retrieval-based methods with generative AI, allowing it to pull specific examples from the user’s background and tailor answers more precisely. RAG excels in delivering in-depth, contextually relevant responses, making it ideal for candidates with rich experience who need to emphasize particular achievements.

- **Chain of Thought (CoT)**: The CoT version focuses on reasoning through multi-step questions. For instance, when generating answers for behavioral questions, the CoT model breaks down the STAR (Situation, Task, Action, Result) format, guiding users through each part of a well-structured response. This version is beneficial for tackling complex questions requiring detailed answers and logical reasoning.

- **Baseline Version**: The baseline model simply calls the LLM API to generate example answers without employing advanced techniques like RAG or CoT. While it still uses the user’s background and job description to create relevant responses, it provides a straightforward, efficient output. This version serves as a foundational approach, ideal for generating initial answer drafts that users can further refine.


### **💯Evaluation Agent**
**Scoring Rubric Development**

Informed by extensive research and insights from data science professionals who have experience with the big tech companies, we developed a comprehensive scoring rubric for evaluating interview responses. This rubric serves as the foundation for assessing user performance within the LiA platform.

**Evaluation Process**

Our Evaluation Agent leverages this scoring rubric to assess user answers to interview questions. Using advanced prompt engineering techniques, the agent provides not only a detailed score but also a clear rationale for each evaluation. This ensures users understand the reasoning behind their scores and receive actionable feedback to improve their responses.



## **🤠LiA's Real Time Information: Tracking Your Confidence in Real-Time**
### **💬Resume Parser**

The first step in the LiA platform is collecting detailed user information, such as experiences and projects, by extracting key details from their resumes. Recognizing the diverse formats of resumes, the system standardizes extracted data for consistency while ensuring user privacy by removing any personal information.


### **🗣️Voice Sensor**
LiA's voice sensor employs advanced audio processing to analyze key vocal characteristics that contribute to interview success. By measuring specific acoustic features in real-time, we provide insights into how your voice may be perceived by interviewers:

- Conversational Flow: Tracks the percentage of unvoiced segments and average pause duration to assess natural speech rhythm and fluency

- Confidence: Measures voice intensity mean to evaluate projected confidence and assertiveness

- Expressiveness: Analyzes fundamental frequency variation (F1 Standard Deviation) to gauge vocal dynamism and engagement

- Voice Modulation: Monitors average frequency band characteristics to detect monotone speech patterns that might indicate nervousness or disengagement

- Clarity: Evaluates the relationship between third and first formant frequencies to assess speech articulation and pronunciation clarity

### **🎦Facial Expression Sensor**
LiA's facial expression sensor leverages state-of-the-art computer vision technology to interpret your non-verbal communication during interviews. Here's how it works:

- Emotion Recognition: The sensor detects micro-expressions and emotional cues, identifying feelings such as happiness, surprise, fear, and confusion. This helps you understand how your emotional responses might be perceived by an interviewer.
  
- Smile Detection: LiA monitors the frequency and authenticity of your smiles. A genuine smile can convey confidence and friendliness, while a lack of smiling may come across as disengagement.
  
- Eye Contact Analysis: Maintaining appropriate eye contact is crucial in building rapport. The sensor tracks your gaze to assess how well you maintain eye contact, providing feedback on your attentiveness and confidence.
  
- Engagement Level: By analyzing a combination of facial movements and expressions, LiA gauges your overall engagement during the interview, highlighting potential ways for overall improvement. 


## **👥LiA's Interface: Your Interview Playground**
LiA's interface is designed to provide an immersive and interactive interview experience that closely mimics real-life scenarios. Here's what you can expect:

- **User-Friendly Design**: The interface features a clean and intuitive layout, making it easy to navigate through different sections such as the about you page, interview, and feedback dashboard.
  
- **Real-Time Video Simulation**: Engage in mock interviews through a video conferencing setup that simulates face-to-face interactions with an interviewer. This prepares you for the dynamics of virtual interviews, which are increasingly common.
  
- **Interactive Feedback Dashboard**: During and after the interview, access a comprehensive dashboard displaying real-time analytics on your performance. Metrics include speech pace, filler word usage, confidence levels, facial expressions, and more.
  
- **Customizable Settings**: Tailor your practice sessions by selecting the type of questions based on your industry, personal information ingestion, and specific skills you want to focus on.
  
- **Playback and Analysis**: Review a dynamic analysis of your mock interviews to self-assess and observe your performance from an interviewer's perspective leading to better outcomes. 

## **🛠️LiA's Toolkit: The Technology Behind the Magic**

**Front-End**: Built with React.js for a responsive and dynamic user experience, ensuring smooth interactions and real-time updates.
**Back-End**: Powered by Flask for handling API requests and integrating AI models, ensuring efficient processing of data and seamless communication between the front-end and back-end.
**AI Integration**: Incorporates Gemini 1.5 Pro for generating questions and providing expert answers, as well as computer vision models for facial expression analysis.


# **💸 LiA's Market Fit and Growth Potential**
LiA is strategically positioned in the rapidly growing job preparation market, particularly in the tech and data science sectors. LiA addresses this need by providing personalized, AI-driven assistance tailored to the unique challenges faced by job seekers. With features like real-time feedback, interactive practice sessions, and emotional intelligence assessments, LiA stands out as a comprehensive solution for users seeking to enhance their interview skills.

**Target Audience**
- **Career Changers**: Individuals like Ben, who are transitioning into data science or tech fields, often face unique challenges in interviews. LiA provides the support they need to bridge knowledge gaps and build confidence.
- **Recent Graduates**: New entrants to the job market require guidance to navigate interview processes. LiA’s tailored question generation helps them prepare effectively for their first interviews.
- **Professionals Seeking Advancement**U: Established professionals aiming for promotions or transitions within their current industry can leverage LiA to refine their interview techniques and demonstrate their growth.

# **🚪Future Works**
**Data Collection and User Insights**

Continuously refine the social skills targets as more user data is gathered. Analyze user behavior to identify which parts of the platform are most engaging. Collect human rubric scores to enhance the accuracy of automated scoring. Additionally, include a dedicated section for users to ask role- or company-specific questions, fostering engagement and clarity.

**Product Enhancement and Feature Expansion**

Optimize audio feature extraction for improved performance and user experience. Expand the knowledge base to encompass a growing number of domains. Further personalize and dynamically adapt question generation to better align with individual user profiles and needs.

# **🛠️Tools Utilized**
| Category | Tool(s) |
|----------|----------|
| Design | Figma, Blender, EEVEE|
| Project Management | Trello |
| Language| Python |
| Frameworks| Flask |
| LLM | Gemini 1.5 Pro |
| Cloud | Google Cloud Platform |

# 👋 About the Team
👩 [Yucheng Fang](https://www.linkedin.com/in/yucheng-fang-49374b170/)

👩🏼 [Khushi Ranganatha](https://www.linkedin.com/in/khushir/)

👨🏼 [Josh Rauvola](https://www.linkedin.com/in/josh-rauvola-250b51168/)

👨🏻 [Ben Thiele](https://www.linkedin.com/in/benthiele1/)
