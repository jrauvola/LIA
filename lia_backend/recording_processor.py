print("ok")
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
import moviepy.editor as mp
import logging
import tempfile
import subprocess
from pydub import AudioSegment
import vertexai
from vertexai.language_models import (TextGenerationModel)
import utility

def recording_processor():
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



        # Save the video file to a temporary location
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_file:
            temp_file.write(video_file.read())
            temp_file_path = temp_file.name
        
        # Extract the audio using ffmpeg
        command = ['ffmpeg', '-v', 'debug', '-i', temp_file_path, '-vn', '-acodec', 'libmp3lame', '-f', 'mp3', '-']
        try:
            audio_data = subprocess.check_output(command, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            app.logger.error(f"Error extracting audio: {e.stderr.decode()}")
            return jsonify({'error': 'Error extracting audio'}), 500
        
        # Delete the temporary video file
        os.unlink(temp_file_path)
        
        audio_file = BytesIO(audio_data)
        audio_file.seek(0)
        
        # Delete the temporary video file
        os.unlink(temp_file_path)
        
        storage_client = storage.Client()
        bucket_name = "lia_audio"
        object_name = f"audio_{datetime.datetime.now().isoformat()}.mp3"
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(object_name)
        blob.upload_from_file(audio_file)
        audio_gcs_uri = f"gs://{bucket_name}/{object_name}"
        
        app.logger.info("Converting audio to text using Google Speech-to-Text API")
        # Convert the audio to text using Google Speech-to-Text API
        try:
            client = speech.SpeechClient()
        
            # Create a RecognitionAudio object and set the URI
            audio = speech.RecognitionAudio(uri=audio_gcs_uri)
        
            # Create a RecognitionConfig object
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.MP3,
                sample_rate_hertz=44100,
                language_code='en-US'
            )
        
            # Make the speech recognition request
            response = client.recognize(config=config, audio=audio)
        
            # Get the transcript from the response
            transcript = response.results[0].alternatives[0].transcript
        except Exception as e:
            app.logger.error(f"Error converting audio to text: {str(e)}")
            return {'error': 'Could not convert audio to text: {0}'.format(e)}
        
        app.logger.info("Saving transcript to 'lia_transcript' bucket")
        # Save the transcript to the 'lia_transcript' bucket
        transcript_file = BytesIO(transcript.encode('utf-8'))
        
        storage_client = storage.Client()
        bucket_name = "lia_transcript"
        object_name = f"transcript_{datetime.datetime.now().isoformat()}.txt"
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(object_name)
        blob.upload_from_file(audio_file)
        audio_url = blob.public_url

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
