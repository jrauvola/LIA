from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import logging
from google.cloud import storage
from google.cloud import speech
import datetime
import os
import pandas as pd
import spacy as sp
import pypdf
import re
from collections import Counter
import PyPDF2 as pypdf
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai import VertexAI
from langchain_google_community import GCSDirectoryLoader
from langchain_google_community import GCSFileLoader
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
# import moviepy.editor as mp
# import logging
# import tempfile
# import subprocess
# from pydub import AudioSegment
import vertexai
from vertexai.language_models import (TextGenerationModel)

# # Define variables for URLs
app = Flask(__name__, static_folder='client/build', static_url_path='')
# CORS(app, resources={r"/*": {"origins": "http://localhost:3000/", "supports_credentials": True}})
logging.basicConfig(level=logging.DEBUG)
CORS(app, resources={
    r"/upload_resume": {
        "origins": "http://localhost:3000",
        "supports_credentials": True # Set to True to allow credentials
    },
    r"/user_recording": {
        "origins": "http://localhost:3000",
        "supports_credentials": True  # Set to True to allow credentials
    }
})

# Enable CORS logging
logging.getLogger('flask_cors').level = logging.DEBUG
# Increase max file size
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

class interview_class:
    def __init__(self, personal_profile, experience, industry, role):
        self.interview_dict = {
            0:  {"question": "Hi I'm Lia! Let's get started. Tell me a little about yourself!",
                 "answer": "",
                 "response": "Okay. Let's jump into the interview."}
        }
        self.personal_profile = {"personal_profile": personal_profile,
                                 "experience": experience, 
                                 "industry": industry, 
                                 "role": role}
        self.evaluator = {},
        self.question_num = 0

    def add_answer(self, new_answer, question_num) -> dict:
        i = question_num
        self.interview_dict[i]["answer"] = new_answer
        return self.interview_dict

    def add_question(self, new_question, question_num) -> dict:
        i = question_num
        self.interview_dict[i] = {"question": new_question}
        return self.interview_dict

    def _repr_(self):
        return (f"Interview Class Instance:\n"
                f"Personal Profile: {self.personal_profile}\n"
                f"Interview Questions: {self.interview_dict}\n"
                f"Evaluator: {self.evaluator}")

### ___________________ RECORDING-TO-TRANSCRIPT ___________________ ###

@app.route('/user_recording', methods=['POST'])
def get_recordings():
    try:
        app.logger.info("Received request at /user_recording endpoint")

        # Get the uploaded webm file from the request
        video_file = request.files.get('file')

        # Check if the file was uploaded
        if not video_file:
            app.logger.error("No file uploaded")
            return jsonify({'error': 'No file uploaded'}), 400

        app.logger.info("Saving video file to 'lia_videos' bucket")
        # # Save the video file to the 'lia_videos' bucket
        # video_url = bucket_save('lia_videos', 'webm', video_file)
        storage_client = storage.Client()
        # Define bucket name and object name (timestamps)
        bucket_name = "lia_videos"
        object_name = f"video_{datetime.datetime.now().isoformat()}.webm"
        bucket = storage_client.bucket(bucket_name)
        # Create and upload a blob object
        blob = bucket.blob(object_name)
        blob.upload_from_file(video_file)
        # Generate the resume URL
        video_url = blob.public_url


        # # Save the video file to a temporary location
        # with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
        #     temp_file.write(video_file.read())
        #     temp_file_path = temp_file.name
        #
        # # Extract the audio using ffmpeg
        # command = ['ffmpeg', '-v', 'debug', '-i', temp_file_path, '-vn', '-acodec', 'libmp3lame', '-f', 'mp3', '-']
        # try:
        #     audio_data = subprocess.check_output(command, stderr=subprocess.PIPE)
        # except subprocess.CalledProcessError as e:
        #     app.logger.error(f"Error extracting audio: {e.stderr.decode()}")
        #     return jsonify({'error': 'Error extracting audio'}), 500
        #
        # # Delete the temporary video file
        # os.unlink(temp_file_path)
        #
        # audio_file = BytesIO(audio_data)
        # audio_file.seek(0)
        #
        # # Delete the temporary video file
        # os.unlink(temp_file_path)
        #
        # storage_client = storage.Client()
        # bucket_name = "lia_audio"
        # object_name = f"audio_{datetime.datetime.now().isoformat()}.mp3"
        # bucket = storage_client.bucket(bucket_name)
        # blob = bucket.blob(object_name)
        # blob.upload_from_file(audio_file)
        # audio_gcs_uri = f"gs://{bucket_name}/{object_name}"
        #
        # app.logger.info("Converting audio to text using Google Speech-to-Text API")
        # # Convert the audio to text using Google Speech-to-Text API
        # try:
        #     client = speech.SpeechClient()
        #
        #     # Create a RecognitionAudio object and set the URI
        #     audio = speech.RecognitionAudio(uri=audio_gcs_uri)
        #
        #     # Create a RecognitionConfig object
        #     config = speech.RecognitionConfig(
        #         encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        #         sample_rate_hertz=44100,
        #         language_code='en-US'
        #     )
        #
        #     # Make the speech recognition request
        #     response = client.recognize(config=config, audio=audio)
        #
        #     # Get the transcript from the response
        #     transcript = response.results[0].alternatives[0].transcript
        # except Exception as e:
        #     app.logger.error(f"Error converting audio to text: {str(e)}")
        #     return {'error': 'Could not convert audio to text: {0}'.format(e)}
        #
        # app.logger.info("Saving transcript to 'lia_transcript' bucket")
        # # Save the transcript to the 'lia_transcript' bucket
        # transcript_file = BytesIO(transcript.encode('utf-8'))
        #
        # storage_client = storage.Client()
        # bucket_name = "lia_transcript"
        # object_name = f"transcript_{datetime.datetime.now().isoformat()}.txt"
        # bucket = storage_client.bucket(bucket_name)
        # blob = bucket.blob(object_name)
        # blob.upload_from_file(audio_file)
        # audio_url = blob.public_url

        print("Question Num")
        # Get the current question_num from the interview instance
        question_num = 0

        transcript = [
            'Hi everyone, I am Katy! My fascination with data began during my graduate studies in Master of Applied Data Science. Witnessing the power of data analysis to uncover hidden patterns and solve complex problems sparked a passion in me I could not ignore.This passion led me to pursue a Master degree in Data Science, where I honed my skills in Python, R, statistical modeling, and machine learning. During my internship at [Company Name], I had the opportunity to work on a project that [briefly describe the project and its impact]. This experience solidified my desire to leverage data science to drive meaningful insights and solutions.',
            'In my previous role, I had to explain the concept of machine learning to our marketing team. I used the analogy of teaching a child to recognize different types of fruit. Just as you would show a child many examples to help them learn, a machine learning model is trained with data. This analogy helped make a complex concept more relatable and easier to understand.',
            'In one project, I worked with a colleague who had a very different working style. To resolve our differences, I scheduled a meeting to understand his perspective. We found common ground in our project goals and agreed on a shared approach. This experience taught me the value of open communication and empathy in teamwork.',
            'In my last role, I had to balance the need for data-driven decisions with ethical considerations. I ensured that all data usage complied with ethical standards and privacy laws, and I presented alternatives when necessary. This approach helped in making informed decisions while respecting ethical boundaries.',
            'In a previous project, the requirements changed frequently. I adapted by maintaining open communication with stakeholders to understand their needs. I also used agile methodologies to be more flexible in my approach, which helped in accommodating changes effectively.',
            'I stay updated by reading industry journals, attending webinars, and participating in online forums. I also set aside time each week to experiment with new tools and techniques. This not only helps me stay current but also continuously improves my skills.'
            ]

        app.logger.info(f"Processing user's answer for question_num: {question_num}")
        # Process the user's answer and add it to the interview.interview_dict
        interview_instance.add_answer(transcript[0], question_num)

        app.logger.info(f"Generating next question for question_num: {question_num + 1}")
        # Generate the next question based on the user's answer
        generate_dynamic_questions(interview_instance, question_num + 1)

        # Get the next question from the interview_dict
        next_question = interview_instance.interview_dict[question_num + 1]["question"]

        app.logger.info("Sending response with uploaded files and next question")
        return jsonify({
            'message': 'Files uploaded successfully',
            'videoUrl': video_url,
            # 'audioUrl': audio_gcs_uri,
            # 'transcriptUrl': transcript_url,
            'nextQuestion': next_question
        })
    except Exception as e:
        app.logger.error(f"Error processing /user_recording: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

### ___________________ RESUME PARSING/STORAGE ___________________ ###

# working order for final reduced text:
# clean_resume_text() <-> clean_text()  
# remove_long_numbers()  
# censor_text()  
# remove_text_before_state()  
# process_resume_text() 

def clean_text(text):
    # input to function should be a string
    
    # Define regular expression pattern to match allowed characters
    pattern = re.compile(r'[^a-z0-9%./]+')
    # Remove unwanted characters from the text
    cleaned_text = re.sub(pattern, ' ', text.lower())
    return cleaned_text # string

def clean_resume_text(file):
    print("Parsing PDF...")

    #read in <FileStorage: 'JR_Tesla_Resume.pdf' ('application/pdf')>
    pdfReader = pypdf.PdfReader(BytesIO(file.read()))
    text = ""
    for page in pdfReader.pages:
        text += page.extract_text()
        # text here is raw resume text (string with no formatting)
    if text:
        # Clean the text
        cleaned_text = clean_text(text)
        return cleaned_text # string
    else:
        print("No text found on this page.")

def process_resume_text(cleaned_text, nlp):
    # lemmatization
    # Process the resume text
    doc = nlp(cleaned_text)

    # Lemmatization and Stemming
    lemmatized_words = [token.lemma_ for token in doc if not token.is_stop]
    
    # return entities, lemmatized_words, top_keywords
    return lemmatized_words # list

def remove_long_numbers(text):
    #remove phone numbers
    # Remove characters like ()-
    cleaned_text = re.sub(r'[-()]+', '', text)
    
    # Look for numbers separated by a space, and only remove that space between consecutive numbers
    cleaned_text = re.sub(r'(\d)\s+(\d)', r'\1\2', cleaned_text)
    
    # Delete numbers with at least 10 digits
    cleaned_text = re.sub(r'\b\d{10,}\b', '', cleaned_text)
    
    return cleaned_text # string

def censor_text(text, words):
# remove user sensitive information
  # Lowercase both text and words for case-insensitive matching
  text_lower = text.lower()
  words_lower = [word.lower() for word in words]

  # Create a set of all possible combinations of words (including single words)
  all_combos = set()
  for word in words_lower:
    all_combos.add(word)
    for i in range(1, len(word)):
      all_combos.add(word[:i] + word[i:])  # Add all substrings

  censored_text = text_lower
  for combo in all_combos:
    # Replace all occurrences of the combination (case-insensitive)
    censored_text = censored_text.replace(combo, "")

  # Return the censored text with the original casing
  return ''.join([c if c.islower() else c.upper() for c in censored_text])

def remove_text_before_state(text):
    # remove text before first state instance, which is usually personal info
    # Define a dictionary mapping state abbreviations to their full names
    state_abbr_to_name = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
        'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
        'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
        'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
        'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
    }
    
    # Create a regex pattern to match state abbreviations and full names
    state_pattern = r'\b(?:' + '|'.join(re.escape(state) for state in state_abbr_to_name.values()) + r'|' + \
                    '|'.join(re.escape(abbr) for abbr in state_abbr_to_name.keys()) + r')\b'
    
    # Find the first occurrence of a state or its abbreviation
    match = re.search(state_pattern, text)
    
    if match:
        # If a match is found, remove all text before it
        return text[match.start()+len(match.group()):]
    else:
        # If no match is found, return the original text
        return text

@app.route('/upload_resume', methods=['POST'])
def upload_resume(): #generate personal profile
    # Get the uploaded file
    uploaded_file = request.files.get('file')

    # Check if no file was uploaded
    if uploaded_file is None:
        return jsonify({'error': 'No file uploaded'}), 400
    
    experience = request.form.get('experience')
    industry = request.form.get('industry')
    role = request.form.get('role')
    nlp = sp.load("en_core_web_sm")

    # problem area start
    clean_text = clean_resume_text(uploaded_file)  
    clean_text = remove_long_numbers(clean_text)
    # clean_text = censor_text(clean_text)
    clean_text = remove_text_before_state(clean_text)
    lemmatized_words = process_resume_text(clean_text, nlp)

    global interview_instance
    interview_instance = interview_class(lemmatized_words, experience, industry, role)

    try: # put in full personal profile IMPORTANT!
        storage_client = storage.Client()
        # Define bucket name and object name (timestamps)
        bucket_name = "lia_resumes"
        object_name = f"resume_lemmatized_{datetime.datetime.now().isoformat()}.txt"
        bucket = storage_client.bucket(bucket_name)
        # Create a blob object
        blob = bucket.blob(object_name)
        # Convert lemmatized words to a string
        lemmatized_text = " ".join(lemmatized_words)
        # Upload the lemmatized text to the bucket
        blob.upload_from_string(lemmatized_text, content_type='text/plain')
        # Generate the resume URL
        resume_url = blob.public_url
        response_data = {
            'message': 'Lemmatized words uploaded successfully',
            'resumeUrl': resume_url
        }
        print("Generating Resume Questions")
        generate_resume_questions()
        print("New Questions: ", interview_instance.interview_dict)
        logging.debug(f"Response data: {response_data}")
        return jsonify(response_data)
       
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'error': 'Failed to save lemmatized words to bucket'}), 500


### ___________________ INTERVIEW PROCESS ___________________ ###

def initialize_rag(project_name, bucket_name, blob):
    print("Loader")
    loader = GCSFileLoader(
    project_name=project_name, 
    bucket=bucket_name,
    blob=blob
    )
    print("Loader: ", loader)
    documents = loader.load()
    print("Documents Loaded")

    embeddings = VertexAIEmbeddings(model_name = "textembedding-gecko@003")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    print("Vector DB")
    vector_db = Chroma.from_documents(docs, embeddings)

    return vector_db

def retrievalQA(retr_docs_num):
    print("Initializing Rag")
    vector_db = initialize_rag(project_name = "adsp-capstone-team-dawn", bucket_name = "lia_rag", blob = "data_science.txt")
    print("Grabbing Retriever")
    retriever = vector_db.as_retriever(
    search_type="similarity", search_kwargs={"k": retr_docs_num} #k: Number of Documents to return, defaults to 4.
    )
    print("Initialize retriever")
    vertexai.init(project="adsp-capstone-team-dawn", location="us-central1")
    print("Grab LLM")
    llm = VertexAI(
    model_name="text-bison-32k",
    max_output_tokens=256,
    temperature=0.1,
    top_p=0.8,
    top_k=40,
    verbose=True,
    )
    print("RETRIEVE")
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    )
    return qa
    
def generate_resume_questions():
    qa_prompt = f"""
                    Context: ```You are a recruiter interviewing a candidate for the data science role. Now you are asking the candidate first question in addition to self introduction ```
                    Prompt: *** Ask the candidate one technical interview question based on Personal Profile. Generate the question as if you are talking to the person. Make the question under 15 words.***
                    Personal Profile: '''{interview_instance.personal_profile}'''
                     """

    print("QA Retrieval")
    qa = retrievalQA(retr_docs_num=4)
    print("QA Response")
    response = qa({"query": qa_prompt})
    
    interview_instance.question_num = interview_instance.question_num + 1
    interview_instance.add_question(response["result"], question_num = interview_instance.question_num)
        
def generate_dynamic_questions(interview_instance, question_num):
    window_dict = {}
    if question_num > 1:
        for key in range(question_num-2, question_num):
            window_dict[key] = interview_instance.interview_dict[key]
    else:
        window_dict = interview_instance.interview_dict
    qa_prompt = f"""
                    Context: ```You are a nice recruiter interviewing a candidate for the data science role. Ask the candidate one follow-up interview question based on there answers recorded in Interview Conversations.```
                    Prompt: *** Ask the candidate one follow-up interview question based on there answers recorded in Interview Conversations. Generate the question as if you are talking to the person. Make sure to react to the candidate's answers. Make the question under 35 words.***
                    Interview Conversations: '''{window_dict}'''
                    Answer: """
    qa = retrievalQA(retr_docs_num=3)
    response = qa({"query": qa_prompt})
     
    question_num = question_num
    interview_instance.add_question(response["result"], question_num = question_num)

def start_interview(): # Generate the first question(s)
    for question_num in range(5):
        # give the question to the front end
        ####################
        if question_num == 0:
            generate_resume_questions(interview)
        elif question_num:
            generate_dynamic_questions(interview, question_num = question_num)
        #get_recordings()
        interview.add_answer(transcript)

# @app.route('/status')
# def status():
#     return 'Ok'

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, host='0.0.0.0', port=80)
