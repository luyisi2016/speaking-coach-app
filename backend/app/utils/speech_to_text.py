from google.cloud import speech
from google.cloud import storage
import uuid
import os

def upload_to_gcs(local_file_path, bucket_name, prefix="uploads/"):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    unique_filename = f"{prefix}{uuid.uuid4()}.flac"
    blob = bucket.blob(unique_filename)
    blob.upload_from_filename(local_file_path)
    return f"gs://{bucket_name}/{unique_filename}"

def transcribe_gcs(gcs_uri: str) -> str:
    """Asynchronously transcribes the audio file from Cloud Storage
    Args:
        gcs_uri: The Google Cloud Storage path to an audio file.
            E.g., "gs://storage-bucket/file.flac".
    Returns:
        The generated transcript from the audio file provided.
    """
 
    print(f"Transcribing from GCS: {gcs_uri}")
    
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,  
        sample_rate_hertz=44100,  
        model="video",
        use_enhanced=True,
        enable_automatic_punctuation=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=180)

    # Collect only the transcript parts
    transcript_parts = [result.alternatives[0].transcript for result in response.results]

    transcript = "".join(transcript_parts)
    print(transcript)

    return transcript



