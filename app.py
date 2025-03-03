from flask import Flask, request, jsonify, send_file, render_template
import asyncio
import edge_tts
import os

app = Flask(__name__)

# Store the event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Output file path
OUTPUT_FILE = "output.mp3"

# Language and voice mapping (example data)
LANGUAGE_NAMES = {
    "ps-AF": "Pashto-Afghanistan",
    "fa-AF": "Persian-Afghanistan",
    "uz-AF": "Uzbek-Afghanistan",
    "sv-AX": "Swedish-Åland Islands",
    "sq-AL": "Albanian-Albania",
    # Add more languages here
}

async def get_available_voices():
    """Fetch available voices from edge_tts and format their names."""
    try:
        voices = await edge_tts.list_voices()
        # Format voice names using LANGUAGE_NAMES
        formatted_voices = []
        for voice in voices:
            language_code = voice["Locale"]
            language_name = LANGUAGE_NAMES.get(language_code, language_code)
            formatted_voices.append({
                "ShortName": voice["ShortName"],
                "Locale": language_code,
                "FriendlyName": f"{voice['ShortName']} ({language_name})"
            })
        return formatted_voices
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return []

@app.route("/")
def home():
    """Serve the HTML page with formatted voices."""
    # Fetch voices dynamically and format their names
    voices = loop.run_until_complete(get_available_voices())
    return render_template("index.html", voices=voices)

@app.route("/speak", methods=["POST"])
def speak():
    """API endpoint to generate and return speech audio."""
    data = request.get_json()
    text = data.get("text", "")
    voice = data.get("voice", "en-US-JennyNeural")  # Default voice

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Generate speech
    success = loop.run_until_complete(generate_speech(text, voice))

    if not success or not os.path.exists(OUTPUT_FILE):
        return jsonify({"error": "Failed to generate speech"}), 500

    # Return the generated audio file
    return send_file(
        OUTPUT_FILE,
        as_attachment=True,
        download_name="speech.mp3",
        mimetype="audio/mpeg"
    )

async def generate_speech(text, voice):
    """Generate speech and save it as an MP3 file."""
    try:
        tts = edge_tts.Communicate(text, voice=voice)
        await tts.save(OUTPUT_FILE)
        return True
    except Exception as e:
        print(f"Error generating speech: {e}")
        return False

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
