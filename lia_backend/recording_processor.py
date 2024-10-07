from google.cloud import speech_v1p1beta1 as speech
from flask import jsonify
import utility
import urllib.parse

def processor(webm_file):
    try:
        print("Processing WebM file in recording_processor")

        # Check if the file was uploaded
        if not webm_file:
            print("WebM file not uploaded")
            return jsonify({'error': 'WebM file not uploaded'}), 400

        # Save WebM file to GCP storage
        print("Saving WebM file to 'lia_recordings' bucket")
        webm_url = utility.gcp_storage_webm(webm_file)

        # Convert HTTPS URL to GCS URI
        gcs_uri = convert_https_to_gcs_uri(webm_url)
        print(f"GCS URI: {gcs_uri}")  # Add this line for debugging

        print("Converting audio to text using Google Speech-to-Text API")
        try:
            client = speech.SpeechClient()

            # Use the GCS URI for the audio file
            audio = speech.RecognitionAudio(uri=gcs_uri)

            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code='en-US',
                enable_automatic_punctuation=True,
                audio_channel_count=1,
                enable_word_time_offsets=True
            )

            # Use long_running_recognize for files longer than 1 minute
            operation = client.long_running_recognize(config=config, audio=audio)

            print("Waiting for operation to complete...")
            response = operation.result(timeout=90)  # Adjust timeout as needed

            # Process the response
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "

            if transcript:
                utility.gcp_storage_transcript(transcript)
                print("Transcript:", transcript)
            else:
                print("No speech recognized in the audio")

            return transcript

        except Exception as e:
            print(f"Error converting audio to text: {str(e)}")
            return None

    except Exception as e:
        print(f"Error processing WebM file: {str(e)}")
        return None


def convert_https_to_gcs_uri(https_url):
    # Parse the URL
    parsed_url = urllib.parse.urlparse(https_url)

    # Extract bucket name and object name
    path_parts = parsed_url.path.lstrip('/').split('/', 1)

    if len(path_parts) == 2:
        bucket_name, object_name = path_parts
        # Decode URL-encoded characters in the object name
        object_name = urllib.parse.unquote(object_name)
        return f"gs://{bucket_name}/{object_name}"
    else:
        raise ValueError(f"Invalid HTTPS URL format: {https_url}")
