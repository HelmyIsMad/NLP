from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import uuid

os.environ["HF_HOME"] = "/tmp/huggingface"
os.environ["WHISPER_CACHE"] = "/tmp/whisper"
os.environ["TRANSFORMERS_CACHE"] = "/tmp/transformers"

app = Flask(__name__)
app.config["INSTANCE_PATH"] = "/tmp"
CORS(app)

model = None

def get_model():
    global model
    if model is None:
        from faster_whisper import WhisperModel
        model = WhisperModel("base.en", device="cpu", compute_type="int8")
    return model

@app.route("/api/health")
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/transcribe", methods=["POST"])
@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    
    tmp_path = f"/tmp/{uuid.uuid4()}.webm"
    audio_file.save(tmp_path)

    try:
        whisper_model = get_model()
        segments, info = whisper_model.transcribe(tmp_path, beam_size=5)
        transcription = " ".join([seg.text for seg in segments])
        return jsonify({"text": transcription, "language": info.language})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)