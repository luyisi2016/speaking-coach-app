from flask import request, jsonify, Blueprint
from ..utils.analysis import analyse_and_store_audio
import os

analyse_bp = Blueprint('analyse_audio', __name__)

@analyse_bp.route('/analyse_audio', methods=['POST'])
def analyse_audio():
    audio_file = request.files.get('audio')

    if not audio_file:
        return jsonify({'error': 'No audio file provided'}), 400

    local_path = f"/tmp/{audio_file.filename}"
    audio_file.save(local_path)

    try:
        transcript_id, transcript, analysis = analyse_and_store_audio(local_path)
        return jsonify({
            'transcript_id': transcript_id,
            'transcript': transcript,
            'analysis': analysis
        })
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
