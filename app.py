import os
import logging
from flask import Flask, request, jsonify
import requests

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Google Gemini API Key (Pastikan ini sudah diatur di Railway Variables)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText"

def get_gemini_response(user_input):
    """Send user input to Google Gemini API and return the response in Indonesian."""
    if not GEMINI_API_KEY:
        return "Saya tidak dapat mengakses AI saat ini. Silakan coba lagi nanti."

    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": {
            "text": f"Jawab dalam bahasa Indonesia dengan jelas: {user_input}"
        }
    }
    
    response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", json=payload, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        return response_data["candidates"][0]["output"]
    else:
        return "Maaf, saya mengalami kesalahan saat memproses permintaan Anda."

@app.route("/", methods=["GET"])
def home():
    return "Google Gemini API for Alexa is running!"

@app.route("/alexa", methods=["POST"])
def alexa_handler():
    """Handle Alexa skill requests."""
    try:
        request_data = request.get_json()
        logger.debug(f"Received Alexa request: {request_data}")

        # Cek tipe request dari Alexa
        request_type = request_data.get("request", {}).get("type")

        if request_type == "LaunchRequest":
            return jsonify(build_alexa_response("Selamat datang! Tanyakan sesuatu kepada saya."))

        elif request_type == "IntentRequest":
            intent_name = request_data["request"]["intent"]["name"]

            if intent_name in ["AMAZON.StopIntent", "AMAZON.CancelIntent"]:
                return jsonify(build_alexa_response("Sampai jumpa!"))

            elif intent_name == "AMAZON.HelpIntent":
                return jsonify(build_alexa_response("Anda bisa bertanya apa saja, dan saya akan menjawab dengan AI."))

            elif intent_name == "AskGeminiIntent":
                user_question = request_data["request"]["intent"]["slots"]["question"]["value"]
                gemini_response = get_gemini_response(user_question)
                return jsonify(build_alexa_response(gemini_response))

            else:
                return jsonify(build_alexa_response("Saya tidak mengerti permintaan Anda."))

        elif request_type == "SessionEndedRequest":
            return jsonify({})

        else:
            return jsonify(build_alexa_response("Permintaan tidak dikenali."))

    except Exception as e:
        logger.error(f"Error processing Alexa request: {e}", exc_info=True)
        return jsonify(build_alexa_response("Terjadi kesalahan saat memproses permintaan Anda."))

def build_alexa_response(output_speech, should_end_session=True):
    """Build a JSON response for Alexa."""
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": output_speech
            },
            "shouldEndSession": should_end_session
        }
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
