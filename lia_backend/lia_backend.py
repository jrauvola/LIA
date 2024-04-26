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