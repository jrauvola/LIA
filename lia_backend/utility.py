from google.cloud import storage

## store resume or personal profile?
def gcp_storage_resume(bucket_name, file):
    storage_client = storage.Client()
    object_name = f"resume_lemmatized_{datetime.datetime.now().isoformat()}.txt"
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

def gcp_storage_resume(bucket_name, file):
    storage_client = storage.Client()
    bucket_name = "lia_videos"
    object_name = f"video_{datetime.datetime.now().isoformat()}.webm"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_file(video_file)
    video_url = blob.public_url
    response_data = {
    'message': 'Lemmatized words uploaded successfully',
    'resumeUrl': resume_url
    }
    return response_data
