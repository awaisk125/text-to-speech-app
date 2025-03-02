from flask import Flask, request, jsonify, send_file, render_template
import asyncio
import edge_tts
import os
import shutil

app = Flask(__name__)

# Store the event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

OUTPUT_FILE = "output.mp3"

# Mapping of language codes to user-friendly language names
LANGUAGE_NAMES = {
    "ps-AF": "Pashto-Afghanistan",
    "fa-AF": "Persian-Afghanistan",
}

async def generate_speech(text, voice, volume):
    """Generate speech and save it as an MP3 file."""
    tts = edge_tts.Communicate(text, voice=voice)
    await tts.save(OUTPUT_FILE)

@app.route("/")
def home():
    """Serve the HTML page."""
    return render_template("index.html", languages=LANGUAGE_NAMES)

@app.route("/speak", methods=["POST"])
def speak():
    """API endpoint to generate and return speech audio."""
    data = request.get_json()
    text = data.get("text", "")
    voice = data.get("voice", "en-US-JennyNeural")  # Default voice
    volume = float(data.get("volume", 100)) / 100  # Convert volume to 0-1 range

    if not text:
        return jsonify({"error": "No text provided"}), 400

    loop.run_until_complete(generate_speech(text, voice, volume))

    if not os.path.exists(OUTPUT_FILE):
        return jsonify({"error": "Failed to generate speech"}), 500

    return send_file(OUTPUT_FILE, as_attachment=True, download_name="speech.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
