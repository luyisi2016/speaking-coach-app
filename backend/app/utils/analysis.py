import spacy
from collections import Counter
from speech_to_text_beta import transcribe_gcs, upload_to_gcs  
from ..db.database import get_db_connection
import json

nlp = spacy.load("en_core_web_sm")

# Filler words to be used in analyse_with_spacy function
FILLER_WORDS = {"um", "uh", "ah", "like", "you know", "I mean", "well", "er", "mmm", "hmm"}

def analyse_with_spacy(transcript_text):

    doc = nlp(transcript_text)

    words = [token.text.lower() for token in doc if token.is_alpha]
    word_count = len(words)
    sentences = list(doc.sents)
    num_sentences = len(sentences)
    avg_sentence_len = sum(len(sent) for sent in sentences) / num_sentences if num_sentences > 0 else 0

    filler_word_count = sum(1 for word in words if word in FILLER_WORDS)

    pos_counts = Counter(token.pos_ for token in doc)

    lemmas = [token.lemma_.lower() for token in doc if token.is_alpha]
    unique_lemmas = set(lemmas)
    ttr = len(unique_lemmas) / len(lemmas) if lemmas else 0

    def token_depth(token):
        depth = 0
        while token.head != token:
            token = token.head
            depth += 1
        return depth

    # Calculate average tree depth for all tokens
    total_depth = sum(token_depth(token) for token in doc)
    avg_tree_depth = total_depth / len(doc) if len(doc) > 0 else 0

    return {
        "word_count": word_count,
        "num_sentences": num_sentences,
        "avg_sentence_length": avg_sentence_len,
        "filler_word_count": filler_word_count,
        "pos_counts": dict(pos_counts),
        "type_token_ratio": round(ttr, 3),
        "avg_syntactic_tree_depth": round(avg_tree_depth, 3),
    }


# This function uses get_db_connection from db.py
def analyze_and_store_audio(local_audio_path, bucket_name="my_audio_bucket_2025"):
    gcs_uri = upload_to_gcs(local_audio_path, bucket_name)
    transcript = transcribe_gcs(gcs_uri)
    analysis = analyse_with_spacy(transcript)

    # Imported DB connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO transcripts (gcs_uri, transcript, analysis)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (gcs_uri, transcript, json.dumps(analysis)),
    )
    transcript_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    print(f"Stored transcript ID: {transcript_id}")
    return transcript_id, transcript, analysis

if __name__ == "__main__":
    local_audio_path = "sample.flac"  # Must be saved locally from the frontend
    analyze_and_store_audio(local_audio_path)
