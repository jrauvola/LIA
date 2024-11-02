from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import logging
import utility
import resume
import os
import interview_processor
import recording_processor
import evaluator
from audio_feature_extraction import update_audio_features
import pandas as pd
from collections import Counter
import tempfile
import subprocess
import logging
from google.cloud import storage
from google.cloud import speech
import datetime

app = Flask(__name__, static_folder='client/build', static_url_path='')
app.config['DEBUG'] = True
logging.basicConfig(level=logging.DEBUG)
CORS(app, resources={
    r"/upload_resume": {
        "origins": "http://localhost:3000",
        "supports_credentials": True
    },
    r"/stop_recording": {
        "origins": "http://localhost:3000",
        "supports_credentials": True
    },
    r"/display_question": {
        "origins": "http://localhost:3000",
        "supports_credentials": True
    },
    r"/generate_question": {
        "origins": "http://localhost:3000",
        "supports_credentials": True
    },
    r"/print_evaluate": {
        "origins": "http://localhost:3000",
        "supports_credentials": True
    },
    r"/start_recording": {
        "origins": "http://localhost:3000",
        "supports_credentials": True
    }
})

class interview_class:
    def __init__(self, personal_profile, experience, industry, role):
        self.interview_dict = {
            0:  {"question": "Hi I'm Lia! Let's get started. Tell me a little about yourself!",
                 "answer": "",
                 "expert_answer": ""}
        }
        self.personal_profile = {"personal_profile": personal_profile,
                                 "experience": experience,
                                 "industry": industry,
                                 "role": role}
        self.evaluator = {}
        self.question_num = 0
        self.answer_num = 0
        self.audio_features = [] ## {feature_1:0.34, feature_2:0.98, audio_len: 13}
        self.video_features = [] ## {feature_1:0.34, feature_2:0.98}
        self.text_features = [] ## {feature_1:0.34, feature_2:0.98, word_count: 13}

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

@app.route('/display_question', methods=['POST'])
def display_question():
    print('display_question question num:', interview_instance.question_num)
    k = interview_instance.question_num
    if k < 5:
        next_question = interview_instance.interview_dict[k]["question"]
        if k == 4:
            interview_instance.question_num = interview_instance.question_num + 1
        return jsonify({
            'nextQuestion': next_question
            })
    else:
        return jsonify({
            'nextQuestion': 'Interview Complete'
            })

@app.route('/print_evaluate', methods=['POST'])
def display_evaluate():
    return jsonify({
        'nextQuestion': evaluator.generate(interview_instance)
    })

@app.route('/generate_question', methods=['POST'])
def generate_question():
    print("triggered")
    i = interview_instance.question_num + 1
    print("initialize retrievalQA")
    qa = interview_processor.retrievalQA()
    print('generate_question question num:', interview_instance.question_num)
    if i <5:
        app.logger.info("Generating")
        if i < 3:
            interview_processor.generate_resume_questions(qa, interview_instance)
        else:
            interview_processor.generate_dynamic_questions(qa, interview_instance)

        interview_instance.question_num = interview_instance.question_num + 1

        return jsonify({'message': 'Question generation requested successfully'}), 200

    else:
        # calling generate() will print the evaluation metrics

        return jsonify({'message': 'No more questions to generate'}), 200


@app.route('/stop_recording', methods=['POST'])
def stop_question():
    try:
        # Get the uploaded WebM file from the request
        webm_file = request.files.get('video')

        if not webm_file:
            return jsonify({'error': 'No WebM file uploaded'}), 400

        j = interview_instance.answer_num
        print('stop_question answer num:', j)

        # Reset file pointer to the beginning of the file
        webm_file.seek(0)

        # Process the WebM file and get the transcript
        transcript, webm_url = recording_processor.processor(webm_file)

        if transcript is None:
            return jsonify({'error': 'Failed to process audio'}), 500

        try:
            print(interview_instance.interview_dict)
            interview_instance.add_answer(transcript, j)

            # Convert HTTPS URL to GCS URI
            gcs_uri = convert_https_to_gcs_uri(webm_url)

            # Update audio features
            update_audio_features(interview_instance, gcs_uri, j)

            print(interview_instance.interview_dict)
            interview_instance.answer_num = j + 1

        except Exception as e:
            print(f"Error in add_answer: {str(e)}")
            return jsonify({'error': 'Failed to add answer'}), 500

        return jsonify({
            'message': 'stop_question success',
            'transcript': transcript,
            'webm_url': webm_url
        })

    except Exception as e:
        print(f"Error in stop_question: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, host='0.0.0.0', port=80)
