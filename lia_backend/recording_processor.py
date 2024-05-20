from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import utility
from google.cloud import storage
from google.cloud import speech
import subprocess
import tempfile
import os
from google.cloud import storage
from io import BytesIO

def processor(video_file, audio_file):
    try:
        print("Received request at /stop_recording endpoint")

        # Check if the files were uploaded
        if not video_file or not audio_file:
            print("Video or audio file not uploaded")
            return jsonify({'error': 'Video or audio file not uploaded'}), 400

        print("Saving video file to 'lia_videos' bucket")
        video_url = utility.gcp_storage_video(video_file)

        print("Saving audio file to 'lia_audio' bucket")
        audio_url = utility.gcp_storage_audio(audio_file)

        print("Converting audio to text using Google Speech-to-Text API")
        try:
            client = speech.SpeechClient()

            # Open the audio file and read its content
            audio_content = audio_file.getvalue()

            # Create the RecognitionAudio object with the audio content
            audio = speech.RecognitionAudio(content=audio_content)

            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=48000,  # Assuming a sample rate of 44.1 kHz
                language_code='en-US'
            )
            response = client.recognize(config=config, audio=audio)

            # Check if the response contains any results
            if not response.results:
                print("No speech recognized in the audio")
                transcript = ""
            else:
                # Access the transcript from the response
                transcript = response.results[0].alternatives[0].transcript
                utility.gcp_storage_transcript(transcript)
                print("Transcript:", transcript)

        except Exception as e:
            print(f"Error converting audio to text: {str(e)}")
            return jsonify({'error': 'Could not convert audio to text: {0}'.format(str(e))}), 500

        print("Returning Transcript")
        return jsonify({
            'message': 'Files uploaded successfully',
            'transcript': transcript
        })
    except Exception as e:
        print(f"Error processing /stop_recording: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500