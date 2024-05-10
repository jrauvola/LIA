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
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
import moviepy.editor as mp

# # Define variables for URLs
app = Flask(__name__, static_folder='client/build', static_url_path='')
CORS(app, resources={r"/*": {"origins": "https://firstapp-4e4b4qv3cq-uc.a.run.app", "supports_credentials": True}}, logging=True)
logging.getLogger('flask_cors').level = logging.DEBUG

# CORS(app, resources={
#     r"/api/upload_resume": {
#         "origins": ["https://firstapp-4e4b4qv3cq-uc.a.run.app", "https://firstapp-4e4b4qv3cq-uc.a.run.app/chatbot", "https://firstapp-4e4b4qv3cq-uc.a.run.app/about-you"],
#         "supports_credentials": True
#     },
#     r"/api/user_recording": {
#         "origins": ["https://firstapp-4e4b4qv3cq-uc.a.run.app", "https://firstapp-4e4b4qv3cq-uc.a.run.app/chatbot", "https://firstapp-4e4b4qv3cq-uc.a.run.app/about-you"],
#         "supports_credentials": True
#     },
#     r"/upload_resume": {
#         "origins": ["https://firstapp-4e4b4qv3cq-uc.a.run.app", "https://firstapp-4e4b4qv3cq-uc.a.run.app/chatbot", "https://firstapp-4e4b4qv3cq-uc.a.run.app/about-you"],
#         "supports_credentials": True
#     },
#     r"/user_recording": {
#         "origins": ["https://firstapp-4e4b4qv3cq-uc.a.run.app", "https://firstapp-4e4b4qv3cq-uc.a.run.app/chatbot", "https://firstapp-4e4b4qv3cq-uc.a.run.app/about-you"],
#         "supports_credentials": True
#     }
# })

# @app.after_request
# def add_cors_headers(response):
#     response.headers.add('Access-Control-Allow-Origin', 'https://firstapp-4e4b4qv3cq-uc.a.run.app')
#     response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
#     response.headers.add('Access-Control-Allow-Credentials', 'true')
#     return response

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
        self.evaluator = {}
        
    def add_answer(self, new_answer, question_num) -> dict:
        i = question_num
        self.interview_dict[i]["answer"] = new_answer
        return self.interview_dict
        
    def add_response(self, new_response) -> dict:
        i = len(self.interview_dict) - 1 
        self.interview_dict[i].update(response=new_response)
        return self.interview_dict
        
    def add_question(self, new_question) -> dict:
        #make new dictionary
        i = len(self.interview_dict)
        self.interview_dict[i] = {"question": new_question, "answer": "", "response": ""}
        return self.interview_dict
    
    def _repr_(self):
        return (f"Interview Class Instance:\n"
                f"Personal Profile: {self.personal_profile}\n"
                f"Interview Questions: {self.interview_dict}\n"
                f"Evaluator: {self.evaluator}")

### ___________________ RECORDING-TO-TRANSCRIPT ___________________ ###

## function to save stuff to buckets
def bucket_save(bucket_name, file_type, uploaded_file):
    # Initialize Google Cloud Storage client
    storage_client = storage.Client()
    # Set the name of your Google Cloud Storage bucket
    bucket = storage_client.bucket(bucket_name)
    # Define object name (timestamps)
    object_name = f"{datetime.datetime.now().isoformat()}.{file_type}"
    # Create a blob object
    blob = bucket.blob(object_name)
    # Upload the file to the bucket
    blob.upload_from_file(uploaded_file)
    # Generate a signed URL for the uploaded recording
    url = blob.generate_signed_url(version='v4', expiration=600, method='GET')
    return url

@app.route('/user_recording', methods=['POST'])
def get_recordings():
    # Get the uploaded webm file from the request
    video_file = request.files.get('file')

    # Check if the file was uploaded
    if not video_file:
        return jsonify({'error': 'No file uploaded'}), 400

    # Save the video file to the 'lia_videos' bucket
    video_url = bucket_save('lia_videos', 'webm', video_file)

    # Use moviepy to extract the audio track from the webm file
    audio = mp.VideoFileClip(video_file)
    audio_file = BytesIO()
    audio.write_audiofile(audio_file, codec='mp3')  # Save the audio track as an mp3 file in memory
    audio_file.seek(0)

    # Save the audio file to the 'lia_audio' bucket
    audio_url = bucket_save('lia_audio', 'mp3', audio_file)

    # Convert the audio to text using Google Speech-to-Text API
    try:
        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(content=audio_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=44100,
            language_code='en-US'
        )
        response = client.recognize(config=config, audio=audio)
        transcript = response.results[0].alternatives[0].transcript
    except Exception as e:
        return {'error': 'Could not convert audio to text: {0}'.format(e)}

    # Save the transcript to the 'lia_transcript' bucket
    transcript_file = BytesIO(transcript.encode('utf-8'))
    transcript_url = bucket_save('lia_transcript', 'txt', transcript_file)

    # Get the current question_num from the interview instance
    question_num = interview_class.question_num

    # Process the user's answer and add it to the interview.interview_dict
    interview.add_answer(transcript, question_num)

    # Generate the next question based on the user's answer
    generate_dynamic_questions(interview_class, question_num + 1)

    # Get the next question from the interview_dict
    next_question = interview_class.interview_dict[question_num + 1]["question"]

    return jsonify({
        'message': 'Files uploaded successfully',
        'videoUrl': video_url,
        'audioUrl': audio_url,
        'transcriptUrl': transcript_url,
        'nextQuestion': next_question
    })

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

def process_resume_text(cleaned_text):
    # lemmatization
    nlp = sp.load("en_core_web_sm") # re-load every fxn call ???

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


def create_interview_class(lemmatized_words, experience, industry, role):
    # Create a new instance of the Interview class
    interview = interview_class(lemmatized_words, experience, industry, role)

    print(interview)
    
    return interview
    
@app.route('/upload_resume', methods=['POST'])
def upload_resume(): #generate personal profile
    # Get the uploaded file
    uploaded_file = request.files.get('file')
    
    experience = request.form.get('experience')
    print("Experience: ", experience)
    industry = request.form.get('industry')
    print("Industry: ", industry)
    role = request.form.get('role')
    print("Role: ", role)
    
    clean_text = clean_resume_text(uploaded_file)
    clean_text = remove_long_numbers(clean_text)
    #clean_text = censor_text(clean_text)
    clean_text = remove_text_before_state(clean_text)
    #clean_text = process_resume_text(clean_text)
    
    lemmatized_words = process_resume_text(clean_text)
    
    global interview_class
    interview_class = create_interview_class(lemmatized_words, experience, industry, role)
    #start_interview here?
    
    # Save the resume file to the 'lia_resumes' bucket
    resume_url = bucket_save('lia_resumes', 'pdf', uploaded_file)
    
    response = jsonify({
        'message': 'Resume processed successfully',
        'resumeUrl': resume_url,
        'interviewInstance': interview_class.__dict__,
        'initialQuestion': interview_class.interview_dict[0]["question"]
    })
    return response

### ___________________ INTERVIEW PROCESS ___________________ ###

def initialize_rag(project_name, bucket_name, prefix):
    loader = GCSDirectoryLoader(
    project_name=project_name, 
    bucket=bucket_name,
    prefix=prefix
    )
    documents = loader.load()

    embeddings = VertexAIEmbeddings(model_name = "textembedding-gecko@003")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    vector_db = Chroma.from_documents(docs, embeddings)

    return vector_db

def retrievalQA(retr_docs_num):
    vector_db = initialize_rag(project_name = "adsp-capstone-team-dawn", bucket_name = "lia_rag", prefix = "data_science")
    retriever = vector_db.as_retriever(
    search_type="similarity", search_kwargs={"k": retr_docs_num} #k: Number of Documents to return, defaults to 4.
    )

    llm = VertexAI(
    model_name="text-bison-32k",
    max_output_tokens=256,
    temperature=0.1,
    top_p=0.8,
    top_k=40,
    verbose=True,
    )  

    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    )
    return qa
    
# def generate_resume_questions(interview_class, question_num):
#     qa_prompt = f"""
#                     Context: ```You are a recruiter interviewing a candidate for the data science role. Now you are asking the candidate first question in addition to self introduction ```
#                     Prompt: *** Ask the candidate one technical interview question based on Personal Profile. Generate the question as if you are talking to the person. Make the question under 15 words.***
#                     Personal Profile: '''{interview_class.personal_profile}'''
#                     Interview Conversations: '''{interview_class.interview_dict}'''
#                      """
#     qa = retrievalQA(retr_docs_num=4)
#     response = qa({"query": qa_prompt})
    
#     question_num = question_num
#     interview_class.add_question(response["result"], question_num = question_num)
        
def generate_dynamic_questions(interview_class, question_num):
    window_dict = {}
    if question_num > 1:
        for key in range(question_num-2, question_num):
            window_dict[key] = interview_class.interview_dict[key]
    else:
        window_dict = interview_class.interview_dict
    qa_prompt = f"""
                    Context: ```You are a nice recruiter interviewing a candidate for the data science role. Ask the candidate one follow-up interview question based on there answers recorded in Interview Conversations.```
                    Prompt: *** Ask the candidate one follow-up interview question based on there answers recorded in Interview Conversations. Generate the question as if you are talking to the person. Make sure to react to the candidate's answers. Make the question under 35 words.***
                    Interview Conversations: '''{window_dict}'''
                    Answer: """
    qa = retrievalQA(retr_docs_num=3)
    response = qa({"query": qa_prompt})
     
    question_num = question_num
    interview_class.add_question(response["result"], question_num = question_num)


# def start_interview(interview): # Generate the first question(s)
#     for question_num in range(5):
#         # give the question to the front end
#         ####################
#         if question_num == 0:
#             generate_resume_questions(interview)
#         elif question_num:
#             generate_dynamic_questions(interview, question_num = question_num)
#         interview.add_answer(transcript)

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, host='0.0.0.0', port=80)