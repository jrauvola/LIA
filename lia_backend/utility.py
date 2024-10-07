from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
import datetime

## store resume or personal profile?
def gcp_storage_resume(file):
    storage_client = storage.Client()
    object_name = f"resume_lemmatized_{datetime.datetime.now().isoformat()}.txt"
    bucket_name = "lia_resumes"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_string(file, content_type='text/plain')
    resume_url = blob.public_url
    response_data = {
        'message': 'Lemmatized words uploaded successfully',
        'resumeUrl': resume_url
        }
    return response_data

#def gcp_storage_audio(bucket_name, file):

def gcp_storage_video(video_file):
    storage_client = storage.Client()
    bucket_name = "lia_videos"
    object_name = f"video_{datetime.datetime.now().isoformat()}.webm"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_file(video_file)
    video_url = blob.public_url
    print("Saved to bucket")
    return video_url

def gcp_storage_audio(audio_file):
    print("Saving audio file to 'lia_audio' bucket")
    storage_client = storage.Client()
    audio_bucket_name = "lia_audio"
    audio_object_name = f"audio_{datetime.datetime.now().isoformat()}.wav"
    audio_bucket = storage_client.bucket(audio_bucket_name)
    audio_blob = audio_bucket.blob(audio_object_name)
    audio_blob.upload_from_file(audio_file)
    audio_url = audio_blob.public_url
    audio_gcs_uri = f"gs://{audio_bucket_name}/{audio_object_name}"
    print("Saved to bucket")
    return audio_gcs_uri

def gcp_storage_transcript(transcript):
    storage_client = storage.Client()
    transcript_bucket_name = "lia_transcript"
    transcript_object_name = f"transcript_{datetime.datetime.now().isoformat()}.txt"
    transcript_bucket = storage_client.bucket(transcript_bucket_name)
    transcript_blob = transcript_bucket.blob(transcript_object_name)
    transcript_blob.upload_from_string(transcript)
    transcript_url = transcript_blob.public_url
    return transcript_url


def gcp_storage_webm(webm_file):
    print("Saving WebM file to 'lia_recordings' bucket")
    try:
        storage_client = storage.Client()
        webm_bucket_name = "lia_recordings"

        # Use a filename format without colons
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S_%f")
        webm_object_name = f"recording_{timestamp}.webm"

        webm_bucket = storage_client.bucket(webm_bucket_name)
        webm_blob = webm_bucket.blob(webm_object_name)
        webm_blob.upload_from_file(webm_file)
        webm_url = webm_blob.public_url
        print(f"WebM file saved to bucket: {webm_url}")
        return webm_url
    except DefaultCredentialsError:
        print("Failed to authenticate. Check your Google Cloud credentials.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return None