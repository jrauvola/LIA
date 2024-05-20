from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import logging
import utility
import resume
import os
import interview_processor
import recording_processor
## import all other files
import pandas as pd
from collections import Counter
import tempfile
import subprocess
import logging
from google.cloud import storage
from google.cloud import speech
import datetime

# # Define variables for URLs
app = Flask(__name__, static_folder='client/build', static_url_path='')
app.config['DEBUG'] = True
# CORS(app, resources={r"/*": {"origins": "http://localhost:3000/", "supports_credentials": True}})
logging.basicConfig(level=logging.DEBUG)
CORS(app, resources={
    r"/upload_resume": {
        "origins": "http://localhost:3000",
        "supports_credentials": True  # Set to True to allow credentials
    },
    r"/stop_recording": {
        "origins": "http://localhost:3000",
        "supports_credentials": True  # Set to True to allow credentials
    },
    r"/display_question": {
        "origins": "http://localhost:3000",
        "supports_credentials": True  # Set to True to allow credentials
    },
    r"/generate_question": {
        "origins": "http://localhost:3000",
        "supports_credentials": True  # Set to True to allow credentials
    },
    r"/start_recording": {
        "origins": "http://localhost:3000",
        "supports_credentials": True  # Set to True to allow credentials
    }
})

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
        self.question_num = 1
        self.answer_num = 0

    def add_answer(self, new_answer, answer_num) -> dict:
        i = answer_num
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


## build personal profile ##
@app.route('/upload_resume', methods=['POST'])
def build_pp():
    uploaded_file = request.files.get('file')

    # Check if no file was uploaded
    if uploaded_file is None:
        return jsonify({'error': 'No file uploaded'}), 400

    experience = request.form.get('experience')
    industry = request.form.get('industry')
    role = request.form.get('role')

    ## create one function to clean resume text
    clean_resume = resume.clean_and_process_resume(uploaded_file)

    global interview_instance
    interview_instance = interview_class(clean_resume, experience, industry, role)

    try: ## replace with storage function
        utility.gcp_storage_resume(clean_resume)
        return jsonify({'success': True}), 200

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({'error': 'Failed to save lemmatized words to bucket'}), 500


## start question ##


@app.route('/display_question', methods=['POST'])
def display_question():
    i = interview_instance.question_num
    if i < 5:
        next_question = interview_instance.interview_dict[i]["question"]

        return jsonify({
            'nextQuestion': next_question
            })
    else:
        return jsonify({
            'nextQuestion': 'The interview is complete.'
            })

@app.route('/generate_question', methods=['POST'])
def generate_question():
    i = interview_instance.question_num
    if i <5:
        app.logger.info("Generating")
        if i < 3:
            interview_processor.generate_resume_question()
        else:
            interview_processor.generate_dynamic_question()
        interview_instance.answer_num = interview_instance.answer_num + 1
        app.logger.info("Generated")
        return jsonify({'message': 'Question generated successfully'}), 200
    else:
        return jsonify({'message': 'No more questions to generate'}), 200


## stop question ##
# '/user_stop_recording' is a fake placeholder endpoint
@app.route('/stop_recording', methods=['POST'])
def stop_question():
    try:
        # Get the uploaded video and audio files from the request
        video_file = request.files.get('video')
        audio_file = request.files.get('audio')
        transcript = recording_processor.processor(video_file, audio_file)
        try:
            j = interview_instance.answer_num
            interview_instance.add_answer(transcript, j)
            interview_instance.answer_num = interview_instance.answer_num + 1
        except Exception as e:
            print(f"Error in add_answer: {str(e)}")
        return jsonify({'message': 'stop_question success'})
    except Exception as e:
        print(f"Error in stop_question: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, host='0.0.0.0', port=80)



