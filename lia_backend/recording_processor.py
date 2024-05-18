from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import utility
from google.cloud import storage
from google.cloud import speech

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
            audio = speech.RecognitionAudio(uri=audio_url)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code='en-US'
            )
            response = client.recognize(config=config, audio=audio)
            transcript = response.results[0].alternatives[0].transcript
        except Exception as e:
            print(f"Error converting audio to text: {str(e)}")
            return {'error': 'Could not convert audio to text: {0}'.format(e)}

        print("Saving transcript to 'lia_transcript' bucket")
        transcript_url = utility.gcp_storage_transcript(transcript)

        # print("Processing user's answer for question_num: {interview_instance.question_num}")
        # interview_instance.add_answer(transcript, interview_instance.question_num)

        print("Sending response with uploaded files and next question")
        return jsonify({
            'message': 'Files uploaded successfully',
            'transcript': transcript
        })
    except Exception as e:
        print(f"Error processing /stop_recording: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500