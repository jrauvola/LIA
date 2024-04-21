from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from google.cloud import storage
import os

app = Flask(__name__, static_folder='client/build', static_url_path='')
CORS(app)

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    # Here you would handle the resume file
    uploaded_file = request.files['file']
    # Save the file and process it
    return jsonify({'message': 'File uploaded successfully'})

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

@app.route('/upload_video', methods=['POST'])

def upload_video():
  # Get the uploaded video file
  uploaded_video = request.files['file']

  # Check if a file was uploaded
  if uploaded_video.filename == '':
    return jsonify({'error': 'No video file uploaded'}), 400

  # Validate file type (optional)
  # You can add logic to check if the uploaded file is a valid video format

  # Generate a unique filename (optional)
  # This helps prevent filename conflicts
  filename = secure_filename(uploaded_video.filename)

  # Create a Cloud Storage client
  storage_client = storage.Client()

  # Define the bucket name
  bucket_name = 'lia_videos' 

  # Create a blob object referring to the video file in the bucket
  bucket = storage_client.bucket(bucket_name)
  blob = bucket.blob(f'videos/{filename}')

  # Upload the video file to the blob
  blob.upload_from_string(uploaded_video.read(), content_type=uploaded_video.content_type)

  # Return a success message
  return jsonify({'message': 'Video uploaded successfully'})
    
@app.route('/get-signed-url', methods=['GET'])
def get_signed_url():
    storage_client = storage.Client()
    bucket = storage_client.bucket('your-gcs-bucket-name')
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
    app.run(use_reloader=True, debug=True, port=5000)
