from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile

os.environ["HF_HOME"] = "/tmp/huggingface"
os.environ["WHISPER_CACHE"] = "/tmp/whisper"

app = Flask(__name__)
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

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
        audio_file.save(tmp_file)
        tmp_path = tmp_file.name

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