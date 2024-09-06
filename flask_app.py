from functools import wraps
from io import BytesIO

from flask import Flask, abort, jsonify, request

import transcribe

app = Flask(__name__)


API_KEYS = {
    "FAKEAPIKEY": "fake-username",
}


def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")
        if api_key in API_KEYS:
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function


@app.post("/transcribe")
@require_api_key
def upload_file():
    api_key = request.headers.get("X-API-KEY")
    user = API_KEYS.get(api_key, "Unknown")
    if user != "Unknown":
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file and file.filename.endswith((".wav", ".ogg", ".mp3", ".mp4", ".m4a")):
            try:
                file_stream = BytesIO(file.read())
                transcriber = transcribe.VoiceTranscriber()
                text = transcriber.transcribe_audio(file_stream)
                return jsonify({"text": text, "user": user}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        return jsonify({"error": "Invalid file type", "body": request}), 400
