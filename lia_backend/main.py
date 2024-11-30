from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import logging
import utility
import resume
import os
import re
import interview_processor
import recording_processor
from recording_processor import convert_https_to_gcs_uri
import evaluator
from audio_feature_extraction import update_audio_features
from text_feature_extraction import update_text_features
from expert_agent import generate_exp_ans_cot
from scoreboard_breakdown import analyze_interview_performance
from scoreboard_breakdown import PerformanceAnalysis
from evaluator import evaluation_class
import pandas as pd
from collections import Counter
import tempfile
import subprocess
import logging
from google.cloud import storage
from google.cloud import speech
import datetime
from video_feature_extraction import update_video_features

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
    },
    r"/process_chunk": {
        "origins": "http://localhost:3000",
        "supports_credentials": True
    },
    r"/get_interview_data": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET"],
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/expert_answer": {
        "origins": "http://localhost:3000",
        "supports_credentials": True
    },
    r"/scoreboard_breakdown": {
        "origins": "http://localhost:3000",
        "supports_credentials": True
    },
    r"/rubric_score": {
        "origins": "http://localhost:3000",
        "supports_credentials": True
    }

})

class interview_class:
    def __init__(self, personal_profile, experience, industry, role, job_description, impressive_project):
        self.interview_dict = {
            0:  {"question": "Hi I'm Lia! Let's get started. Tell me a little about yourself!",
                 "answer": "",
                 "expert_answer": ""}
        }
        self.personal_profile = {
            "personal_profile": personal_profile,
            "experience": experience,
            "industry": industry,
            "role": role,
            "job_description": job_description,
            "impressive_project": impressive_project
        }
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

    # Get all form fields
    experience = request.form.get('experience')
    industry = request.form.get('industry')
    role = request.form.get('role')
    job_description = request.form.get('job_description')
    impressive_project = request.form.get('impressive_project')

    ## create one function to clean resume text
    clean_resume = resume.clean_and_process_resume(uploaded_file)

    global interview_instance
    interview_instance = interview_class(clean_resume, experience, industry, role, job_description, impressive_project)

    global evaluation_instance
    evaluation_instance = evaluation_class()

    global performance_instance
    performance_instance = PerformanceAnalysis()

    print("initialize retrievalQA")
    global qa
    qa = interview_processor.retrievalQA()

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
    eval_response = evaluator.eval_input(interview_instance, interview_instance.question_num)
    return jsonify({'evaluation': eval_response})

@app.route('/generate_question', methods=['POST'])
def generate_question():
   print("triggered")
   global qa
   i = interview_instance.question_num + 1
   print('generate_question question num:', interview_instance.question_num)
   if i < 5:
       app.logger.info("Generating")
       if i == 1:
           interview_processor.generate_resume_questions(qa, interview_instance)
       elif i == 2:
           interview_processor.generate_job_specific_question(interview_instance)
       elif i == 3:
           interview_processor.generate_super_technical_question(qa, interview_instance)
       else:
           interview_processor.generate_dynamic_questions(qa, interview_instance)

       interview_instance.question_num = interview_instance.question_num + 1

       return jsonify({'message': 'Question generation requested successfully'}), 200

   else:
       # calling generate() will print the evaluation metrics
       return jsonify({'message': 'No more questions to generate'}), 200


@app.route('/stop_recording', methods=['POST'])
def stop_question():
    print("stop_question triggered")
    try:
        # Get the uploaded WebM file and transcript from the request
        webm_file = request.files.get('video')
        transcript = request.form.get('transcript')  # Get transcript from form data

        if not webm_file:
            return jsonify({'error': 'No WebM file uploaded'}), 400

        j = interview_instance.answer_num
        print('stop_question answer num:', j)

        # Reset file pointer to the beginning of the file
        webm_file.seek(0)

        # Save WebM file and get URL
        webm_url = utility.gcp_storage_webm(webm_file)

        if not transcript:
            # Fallback to audio processing if no transcript provided
            transcript, _ = recording_processor.processor(webm_file)

        if transcript is None:
            return jsonify({'error': 'Failed to process audio'}), 500

        # Store the answer
        print(interview_instance.interview_dict)
        interview_instance.add_answer(transcript, j)

        # Convert HTTPS URL to GCS URI
        gcs_uri = convert_https_to_gcs_uri(webm_url)

        # Update audio features and capture audio length
        audio_features = update_audio_features(interview_instance, gcs_uri, j)
        audio_length = interview_instance.audio_features[j]['audio_length'] if audio_features else 0

        print("Audio features extracted:", interview_instance.audio_features)

        # Update text features with audio length
        update_text_features(interview_instance, transcript, audio_length, j)

        # Update video features
        webm_file.seek(0)  # Reset file pointer
        video_features = update_video_features(interview_instance, webm_file, j)

        # Generate and store expert answer
        current_question = interview_instance.interview_dict[j]["question"]
        expert_response = generate_exp_ans_cot(current_question, qa, interview_instance)
        interview_instance.interview_dict[j]["expert_answer"] = expert_response
        print("Expert answer generated and stored:", expert_response)

        # Get and parse evaluation response
        eval_response = evaluator.eval_input(interview_instance, j)

        # Store in evaluation instance
        evaluation_instance.evaluation_dict[j] = eval_response

        print("Complete evaluation dictionary:", evaluation_instance.evaluation_dict)
        print("Features extracted:")
        print("Audio:", interview_instance.audio_features)
        print("Text:", interview_instance.text_features)
        print("Video:", interview_instance.video_features)

        interview_instance.answer_num = j + 1

        return jsonify({
            'message': 'stop_question success',
            'transcript': transcript,
            'webm_url': webm_url,
            'expert_answer': expert_response,
            'evaluation': eval_response
        })

    except Exception as e:
        print(f"Error in stop_question: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/process_chunk', methods=['POST']) #may remove
def process_chunk():
    print("🎤 process_chunk: Received new audio chunk")
    audio_chunk = request.files.get('audio')
    
    if not audio_chunk:
        print("❌ process_chunk: No audio chunk received")
        return jsonify({'error': 'No audio chunk uploaded'}), 400

    content = audio_chunk.read()
    print(f"📊 process_chunk: Audio content size: {len(content)} bytes")
    
    # Create speech client
    client = speech.SpeechClient()
    
    # Update recognition config with explicit sample rate
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        language_code="en-US",
        enable_automatic_punctuation=True,
        model="default",
        sample_rate_hertz=16000  # Add explicit sample rate
    )

    try:
        # Create audio object
        audio = speech.RecognitionAudio(content=content)

        print("🚀 process_chunk: Sending request to Speech-to-Text API")
        response = client.recognize(config=config, audio=audio)
        
        interim_transcript = ""
        is_final = False
        
        print("📝 process_chunk: Processing recognition results")
        for result in response.results:
            if result.alternatives:
                transcript_piece = result.alternatives[0].transcript
                confidence = result.alternatives[0].confidence
                is_final = result.is_final
                print(f"✨ process_chunk: Found transcript piece: {transcript_piece} (confidence: {confidence})")
                interim_transcript += transcript_piece + " "
        
        print(f"✅ process_chunk: Final transcript: {interim_transcript.strip()}")
        
        return jsonify({
            'interimTranscript': interim_transcript.strip(),
            'isFinal': is_final
        })

    except Exception as e:
        print(f"❌ process_chunk: Error processing audio: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/get_interview_data', methods=['GET'])
def get_interview_data():
    try:
        if interview_instance:
            return jsonify({
                'interview_dict': interview_instance.interview_dict,
                'audio_features': interview_instance.audio_features,
                'video_features': interview_instance.video_features,
                'text_features': interview_instance.text_features
            })
        else:
            return jsonify({'error': 'No interview data available'}), 404
    except Exception as e:
        print(f"Error getting interview data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/expert_answer', methods=['GET'])
def get_expert_answer():
    try:
        # Get question number from query parameter, default to 0
        question_num = request.args.get('question_num', 0, type=int)

        # Validate question exists
        if question_num not in interview_instance.interview_dict:
            return jsonify({'error': f'Question {question_num} not found'}), 404

        # Get question and expert answer
        question = interview_instance.interview_dict[question_num]["question"]
        answered_questions = sum(1 for q in interview_instance.interview_dict.values() 
                        if "answer" in q and q["answer"])
        expert_answer = interview_instance.interview_dict[question_num]["expert_answer"]

        # Get total number of questions for frontend navigation
        total_questions = len(interview_instance.interview_dict)

        return jsonify({
            'question': question,
            'expert_answer': expert_answer,
            'current_question': question_num,
            'total_questions': answered_questions
        })
    except Exception as e:
        print(f"Error getting expert answer: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/rubric_score', methods=['GET'])
def get_rubric_score():
    try:
        question_num = request.args.get('question_num', 0, type=int)

        if question_num not in evaluation_instance.evaluation_dict:
            return jsonify({'error': f'Evaluation for question {question_num} not found'}), 404

        question_evaluation = evaluation_instance.evaluation_dict[question_num]

        # Ensure proper structure
        categories = [
            "Relevance to the Question",
            "Technical Correctness",
            "Completeness of the Answer",
            "Anecdotal Element"
        ]

        # Structure the response with proper keys
        response_data = {
            'question_num': question_num,
            'total_questions': len(evaluation_instance.evaluation_dict),
            'rubric_categories': {
                cat: {
                    'Score': question_evaluation[cat]['Score'],
                    'Justification': question_evaluation[cat]['Justification']
                } for cat in categories if cat in question_evaluation
            }
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error getting rubric scores for question {question_num}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/scoreboard_breakdown', methods=['GET'])
def get_scoreboard_breakdown():
    try:
        # Check if interview has data
        if not interview_instance.text_features or not interview_instance.audio_features or not interview_instance.video_features:
            return jsonify({'error': 'No interview data available'}), 404

        # Calculate averages for all features
        def calculate_averages():
            # Text features averages
            text_metrics = {
                'quantifier_words_pct': 0,
                'filler_nonfluency_pct': 0,
                'wpsec': 0,
                'upsec': 0
            }

            for features in interview_instance.text_features:
                for metric in text_metrics:
                    text_metrics[metric] += features.get(metric, 0)

            text_count = len(interview_instance.text_features)
            for metric in text_metrics:
                text_metrics[metric] = text_metrics[metric] / text_count if text_count > 0 else 0

            # Audio features averages
            audio_metrics = {
                'avgBand1': 0,
                'unvoiced_percent': 0,
                'f1STD': 0,
                'f3meanf1': 0,
                'intensityMean': 0,
                'avgDurPause': 0
            }

            for features in interview_instance.audio_features:
                for metric in audio_metrics:
                    audio_metrics[metric] += features.get(metric, 0)

            audio_count = len(interview_instance.audio_features)
            for metric in audio_metrics:
                audio_metrics[metric] = audio_metrics[metric] / audio_count if audio_count > 0 else 0

            # Video features averages
            video_metrics = {
                'blink_rate': 0,
                'average_smile_intensity': 0,
                'average_engagement': 0,
                'average_stress': 0
            }

            for features in interview_instance.video_features:
                for metric in video_metrics:
                    video_metrics[metric] += features.get(metric, 0)

            video_count = len(interview_instance.video_features)
            for metric in video_metrics:
                video_metrics[metric] = video_metrics[metric] / video_count if video_count > 0 else 0

            return {**text_metrics, **audio_metrics, **video_metrics}

        try:
            # Get averaged metrics
            user_metrics = calculate_averages()

            # Create and populate performance analysis
            global performance_instance
            performance_instance = PerformanceAnalysis()
            analysis_dict = analyze_interview_performance(user_metrics, qa)

            # Store the analysis in our global instance
            performance_instance.analysis_dict = analysis_dict

            # Return the structured analysis dictionary
            return jsonify({
                'analysis': performance_instance.analysis_dict
            })

        except Exception as e:
            print(f"Error in analysis: {str(e)}")
            # Return empty structured response if analysis fails
            return jsonify({
                'analysis': PerformanceAnalysis().analysis_dict
            }), 500

    except Exception as e:
        print(f"Error getting scoreboard breakdown: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(use_reloader=True, debug=True, host='0.0.0.0', port=80)
