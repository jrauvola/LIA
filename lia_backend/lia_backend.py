from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from google.cloud import storage
import datetime
import os

# Define variables for URLs

app = Flask(__name__, static_folder='client/build', static_url_path='')
CORS(app, resources={
    r"/upload_resume": {
        "origins": "https://firstapp-4e4b4qv3cq-uc.a.run.app",
        "supports_credentials": True  # Set to True to allow credentials
    },
    r"/submit_about": {
        "origins": "https://firstapp-4e4b4qv3cq-uc.a.run.app",
        "supports_credentials": True  # Set to True to allow credentials
    }
})


@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    # Get the uploaded file
    uploaded_file = request.files.get('file')

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
