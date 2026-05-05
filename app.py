from flask import Flask, request, jsonify, send_from_directory
from faster_whisper import WhisperModel
import os
import tempfile

app = Flask(__name__)

model = WhisperModel("base", device="cpu", compute_type="int8")

@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")

@app.route("/script.js")
def script():
    return send_from_directory("frontend", "script.js")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
        audio_file.save(tmp_file)
        tmp_path = tmp_file.name

    try:
        segments, info = model.transcribe(tmp_path, beam_size=5)
        transcription = " ".join([seg.text for seg in segments])
        return jsonify({"text": transcription, "language": info.language})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    app.run(debug=True, port=5000)