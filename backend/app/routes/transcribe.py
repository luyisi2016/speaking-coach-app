from flask import Flask, request, jsonify, Blueprint
from ..utils import speech_to_text
import os

transcribe_bp = Blueprint('upload_audio', __name__)


@transcribe_bp.route('/upload_audio', methods=['POST'])
def upload_audio():
    audio_file = request.files.get('audio')

    if not audio_file:
        return jsonify({"error": "No audio file provided"}), 400

    # Save locally temporarily
    local_path = f"/tmp/{audio_file.filename}" # Should be the temp folder of my render container
    audio_file.save(local_path)

    try:

        gcs_uri = speech_to_text.upload_to_gcs(local_path, "my_audio_bucket_2025")

        transcript = speech_to_text.transcribe_gcs(gcs_uri)

        return jsonify({'transcript':transcript})
    
    finally:
        if os.path.exists(local_path): # Cleanup local file
            os.remove(local_path)