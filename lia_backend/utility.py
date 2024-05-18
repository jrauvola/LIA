from google.cloud import storage
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