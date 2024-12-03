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
5. [Interview Journey with LiA](#Interview-Journey-with-LiA)
   * [Customized Experience](#Customized-Experience)
   * [Interactive Session](#Interactive-Session)
   * [Personal Feedback](#Personal-Feedback)
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

#### **How It Works**

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

Our Evaluation Agent, leverages this scoring rubric to assess the user's answers to interview questions. By utilizing advanced prompt engineering techniques, LiA provides detailed feedback highlighting areas where the user may be lacking and offers specific guidance on how to enhance their responses.


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

The voice sensor provides real-time feedback through an intuitive dashboard, allowing users to visualize these metrics during practice sessions and track improvements over time.

### **🎦Facial Expression Sensor**
LiA's facial expression sensor leverages state-of-the-art computer vision technology to interpret your non-verbal communication during interviews. Here's how it works:

- **Emotion Recognition**: The sensor detects micro-expressions and emotional cues, identifying feelings such as happiness, surprise, fear, and confusion. This helps you understand how your emotional responses might be perceived by an interviewer.
  
- **Smile Detection**: LiA monitors the frequency and authenticity of your smiles. A genuine smile can convey confidence and friendliness, while a lack of smiling may come across as disengagement.
  
- **Eye Contact Analysis**: Maintaining appropriate eye contact is crucial in building rapport. The sensor tracks your gaze to assess how well you maintain eye contact, providing feedback on your attentiveness and confidence.
  
- **Engagement Level**: By analyzing a combination of facial movements and expressions, LiA gauges your overall engagement during the interview, highlighting potential ways for overall improvement. 

The facial expression sensor offers real-time feedback through an intuitive interface, allowing you to adjust your non-verbal cues to best prepare yourself for your future interview!

**Overall:** These metrics are displayed in real-time alongside the voice analysis, giving users comprehensive feedback on both verbal and non-verbal aspects of their interview performance. The system also provides gentle prompts when it detects extended periods of minimal eye contact or neutral expressions, helping users develop more engaging interview presence.

## **👥LiA's Interface: Your Interview Playground**
LiA's interface is designed to provide an immersive and interactive interview experience that closely mimics real-life scenarios. Here's what you can expect:

- **User-Friendly Design**: The interface features a clean and intuitive layout, making it easy to navigate through different sections such as the about you page, interview, and feedback dashboard.
  
- **Real-Time Video Simulation**: Engage in mock interviews through a video conferencing setup that simulates face-to-face interactions with an interviewer. This prepares you for the dynamics of virtual interviews, which are increasingly common.
  
- **Interactive Feedback Dashboard**: During and after the interview, access a comprehensive dashboard displaying real-time analytics on your performance. Metrics include speech pace, filler word usage, confidence levels, facial expressions, and more.
  
- **Customizable Settings**: Tailor your practice sessions by selecting the type of questions based on your industry, personal information ingestion, and specific skills you want to focus on.
  
- **Playback and Analysis**: Review a dynamic analysis of your mock interviews to self-assess and observe your performance from an interviewer's perspective leading to better outcomes. 

### Tech Stack Highlights:

- **Front-End**: Built with React.js for a responsive and dynamic user experience, ensuring smooth interactions and real-time updates.
- **Back-End**: Powered by Flask for handling API requests and integrating AI models, ensuring efficient processing of data and seamless communication between the front-end and back-end.
- **AI Integration**: Incorporates LLMs for generating questions and providing expert answers, as well as computer vision models for facial expression analysis.

LiA's interface serves as a comprehensive playground where you can hone your interview skills in a controlled, feedback-rich environment, ultimately boosting your confidence and readiness for actual interviews.

# **🗺️Interview Journey with LiA**

The Interview Journey with LiA begins when users share their professional background and target job description, enabling LiA to craft a personalized interview experience that bridges their past experience with their desired role. After a brief animation sequence, users are transported into a simulated video call environment where they see themselves in a small frame, with LiA's lifelike presence commanding most of the screen. The interview unfolds across five carefully curated questions, with users noticing an increasing level of personalization as they progress. This deepening relevance stems from LiA's sophisticated ability to incorporate previous responses, analyzing transcripts and user information to generate increasingly targeted questions after the initial standardized opener.

Following the interview, users are guided through a comprehensive three-part feedback experience. The journey begins with the Social Skills Feedback section, where users encounter a detailed scoreboard evaluating their communication style, vocal qualities, and overall demeanor—leveraging LiA's advanced capacity to analyze not just verbal content but also audio and visual cues. Next, the Technical Skills Feedback screen provides clear thumbs-up or thumbs-down assessments for technical responses, mirroring evaluation methods used by leading technology companies. The experience culminates in an interactive transcript review where users can compare their responses against expert-crafted answers generated by the Gemini LLM, complete with specific improvement recommendations from LiA. Users can then choose to restart the process, armed with these insights, to refine their interview performance across all dimensions.

## **📷Customized Experience**

LiA distinguishes itself from traditional interview preparation tools through its ability to create a deeply personalized experience that adapts to each user's unique professional background and career aspirations.

At the heart of the application lies a sophisticated question generation system that creates a uniquely tailored interview experience for each user. While the first question serves as a standardized opener, the subsequent four questions are dynamically generated based on a rich combination of inputs: the user's provided background information, the target job description, and most impressively, the actual transcripts from previous answers within the same session. This creates an increasingly personalized interview path where each question builds meaningfully upon the last, simulating the natural flow of a real technical interview.

The application's evaluation systems are equally customized, with both technical and social skills assessments adapting to the specific requirements of the user's target role. The technical assessment criteria are carefully calibrated to mirror the actual hiring processes of major tech companies, with evaluation metrics and feedback specifically tuned to the user's intended domain, whether it be frontend development, backend engineering, or machine learning. Similarly, the social skills analysis employs a sophisticated multimodal approach, analyzing verbal content, audio characteristics, and visual cues, with the importance of each factor weighted according to the specific demands of the target role—for instance, placing higher emphasis on communication style for customer-facing positions.

The final layer of customization appears in the application's feedback and improvement systems. Rather than providing genKhushi "perfect answers," the system generates expert responses that precisely match the technical depth, communication style, and specific requirements of the target role and company. This customization extends into the improvement pathway, where the feedback loop prioritizes suggestions based on the user's most significant areas for growth. The system maintains a memory of previous performance metrics, allowing users to track their progress over time and focus their practice on the areas that will most impact their interview success.

## **🎹Interactive Session**

The user's interactive journey with LiA begins at the "About You" interface, where they actively shape their upcoming interview experience by providing key information about their background, skills, and aspirations. This initial interaction goes beyond simple form-filling – users engage in a dynamic process of describing their professional journey and uploading their target job description, each input helping to craft the parameters of their personalized mock interview experience.

The heart of user interaction occurs during the mock interview itself, where users engage with LiA in a uniquely unpredictable conversation. Unlike traditional interview prep tools with pre-scripted questions, users must think on their feet as they respond to LiA's dynamically generated questions. This creates a genuinely interactive experience where each answer influences the AI's generation of subsequent questions, making every interview session unique and challenging in its own way. The real-time video interface, complete with the user's self-view window, adds another layer of interactivity as users must manage both their verbal responses and visual presentation.

The final interactive component empowers users to take control of their learning journey through an extensive feedback exploration system. Users can navigate through various performance metrics, drilling down into specific areas where improvement is needed. This interactive feedback system allows users to toggle between different scorecards, compare their responses with expert answers, and deeply examine areas marked for improvement. This self-directed exploration enables users to focus their attention on the aspects of their interview performance that need the most work, creating a personalized learning experience that extends beyond the interview itself.

## **📨Personal Feedback**
**User Performance Evaluation**

In the final stage of the LiA platform, users receive a comprehensive evaluation of their performance, highlighting both strengths and areas for improvement. LiA assesses various qualitative and quantitative features, providing users with insights into their conversational flow and the relevance of their answers to posed questions.

**Comprehensive Feedback Mechanism**

LiA goes beyond basic assessments by offering tailored feedback on how users can enhance their qualitative responses. This includes guidance on the technical correctness of their answers and adherence to effective response structures. By focusing on these critical aspects, users are equipped with actionable insights that promote skill development and confidence in their conversational abilities.

# **💸 LiA's Market Fit and Growth Potential**
**Market Fit**
LiA is strategically positioned in the rapidly growing job preparation market, particularly in the tech and data science sectors. As more individuals pivot to tech-related careers, the demand for effective interview preparation tools has surged. LiA addresses this need by providing personalized, AI-driven assistance tailored to the unique challenges faced by job seekers. With features like real-time feedback, interactive practice sessions, and emotional intelligence assessments, LiA stands out as a comprehensive solution for users seeking to enhance their interview skills.

**Target Audience**
LiA caters to a diverse audience, including:

- **Career Changers**: Individuals like Ben, who are transitioning into data science or tech fields, often face unique challenges in interviews. LiA provides the support they need to bridge knowledge gaps and build confidence.
- **Recent Graduates**: New entrants to the job market require guidance to navigate interview processes. LiA’s tailored question generation helps them prepare effectively for their first interviews.
- **Professionals Seeking Advancement**U: Established professionals aiming for promotions or transitions within their current industry can leverage LiA to refine their interview techniques and demonstrate their growth.

# **🚪Future Works**


# **🛠️Tools Utilized**
| Category | Tool(s) |
|----------|----------|
| Design | Figma |
| Language| Python |
| Frameworks| Flask |
| LLM | Gemini 1.5 Pro |
| Cloud | GCP |

# 👋 About the Team
👩 Yucheng

👩🏼 Khushi

👨🏼 Josh

👨🏻 Ben
