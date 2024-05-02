from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from google.cloud import storage
import datetime
import os
import pandas as pd
import spacy as sp
import pypdf
import re
from collections import Counter
import PyPDF2 as pypdf
from io import BytesIO


class interview_class:
    def __init__(self, personal_profile):
        self.prompt = ['prompt 1','prompt 2']
        self.interview_dict = {
            0:  {"question": "Hi I'm Lia, let's get started. Tell me a little about yourself!",
                 "answer": "",
                 "response": "Okay. Let's jump into the interview."}
        }
        self.personal_profile = personal_profile
        self.evaluator = {}
    
    def add_answer(self, interview_dict: dict, answer) -> dict:
        self.interview_dict = interview_dict
        return self.interview_dict
        
    def add_response(self, interview_dict: dict, response) -> dict:
        self.interview_dict = interview_dict
        return self.interview_dict
        
    def add_question(self, interview_dict: dict, question) -> dict:
        self.interview_dict = interview_dict
        return self.interview_dict
    
    
    def _repr_(self):
        return (f"Interview Class Instance:\n"
                f"Personal Profile: {self.personal_profile}\n"
                f"Prompts: {self.prompt}\n"
                f"Interview Questions: {self.interview_dict}\n"
                f"Evaluator: {self.evaluator}")

# Define variables for URLs
GOOGLE_ORIGINS = 'https://firstapp-4e4b4qv3cq-uc.a.run.app'
GOOGLE_CREDENTIALS = True

LOCAL_ORIGINS = 'http://localhost:3000'
LOCAL_CREDENTIALS = True

if os.getenv('GAE_ENV', '').startswith('standard'):
    # Production environment
    ORIGINS = GOOGLE_ORIGINS
    CREDENTIALS = GOOGLE_CREDENTIALS
else:
    # Local development environment
    ORIGINS = LOCAL_ORIGINS
    CREDENTIALS = LOCAL_CREDENTIALS

print(f'ORIGINS: {ORIGINS}\n'
      f'CREDENTIALS: {CREDENTIALS}')

app = Flask(__name__, static_folder='client/build', static_url_path='')
CORS(app, resources={
    r"/upload_resume": {
        "origins": ORIGINS,
        "supports_credentials": CREDENTIALS  # Set to True to allow credentials
    },
    r"/submit_about": {
        "origins": ORIGINS,
        "supports_credentials": CREDENTIALS  # Set to True to allow credentials
    }
})


### ___________________ RESUME PARSING/STORAGE ___________________ ###

def store_resume(uploaded_file):
    # Check if the file was uploaded
    if not uploaded_file:
        return jsonify({'error': 'No file uploaded'}), 400

    # Create a Cloud Storage client
    storage_client = storage.Client()

    # Define bucket name and object name (timestamps)
    bucket_name = "lia_resumes"
    object_name = f"resume_{datetime.datetime.now().isoformat()}.pdf"
    
    bucket = storage_client.bucket(bucket_name)
    
    # Create a blob object
    blob = bucket.blob(object_name)

    # Upload the file to the bucket
    blob.upload_from_file(uploaded_file)
    
    # Save the file and process it
    return jsonify({'message': 'File uploaded successfully'})

def clean_text(text):
    # Define regular expression pattern to match allowed characters
    pattern = re.compile(r'[^a-z0-9%./]+')
    # Remove unwanted characters from the text
    cleaned_text = re.sub(pattern, ' ', text.lower())
    return cleaned_text

def clean_resume_text(file):
    print("Parsing PDF...")

    #read in <FileStorage: 'JR_Tesla_Resume.pdf' ('application/pdf')>
    pdfReader = pypdf.PdfReader(BytesIO(file.read()))
    text = ""
    for page in pdfReader.pages:
        text += page.extract_text()
    if text:
        # Clean the text
        cleaned_text = clean_text(text)
        return cleaned_text
    else:
        print("No text found on this page.")

def process_resume_text(cleaned_text):
    nlp = sp.load("en_core_web_sm")

    # Process the resume text
    doc = nlp(cleaned_text)

    # Lemmatization and Stemming
    lemmatized_words = [token.lemma_ for token in doc if not token.is_stop]
    
    # return entities, lemmatized_words, top_keywords
    return lemmatized_words

def create_interview_class(lemmatized_words):
    # Create a new instance of the Interview class
    interview = interview_class(lemmatized_words)

    print(interview)
    
    return interview
    
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    # Get the uploaded file
    uploaded_file = request.files.get('file')

    clean_text = clean_resume_text(uploaded_file)
    
    lemmatized_words = process_resume_text(clean_text)

    create_interview_class(lemmatized_words)

    #store_resume(uploaded_file)

    return jsonify({'message': 'File Parsed successfully'})


### ___________________ INTERVIEW PROCESS ___________________ ###

def generate_questions():
    # Generate questions based on the resume
    pass

def start_interview(interview):
    # Start the interview
    pass


@app.route('/submit_about', methods=['POST'])
def submit_about():
    # Here you would handle the form data
    data = request.json
    # Save the data and/or perform actions
    return jsonify({'message': 'Data received'})

@app.route('/api/get_initial_assessment', methods=['GET'])
def get_initial_assessment():
    # Return initial assessment data
    pass

@app.route('/api/send_message', methods=['POST'])
def send_message():
    # Send message to chatbot and get response
    pass

@app.route('/get-signed-url', methods=['GET'])
def get_signed_url():
    storage_client = storage.Client()
    bucket = storage_client.bucket('lia_videos')
    blob = bucket.blob('videos/video.webm')

    url = blob.generate_signed_url(version='v4', expiration=600, method='PUT')

    return jsonify({'signedUrl': url})

@app.route('/api/toggle_theme', methods=['POST'])
def toggle_theme():
    # Handle theme toggling
    pass

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')



if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, host='0.0.0.0', port=80)
