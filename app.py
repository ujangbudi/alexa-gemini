import os
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

@app.route("/", methods=["GET"])
def home():
    return "Google Gemini API for Alexa is running!"

@app.route("/alexa", methods=["POST"])
def alexa_handler():
    """Handle Alexa skill requests and respond using Google Gemini API."""
    
    # Debugging: Log request headers & body
    logging.debug(f"Headers: {request.headers}")
    logging.debug(f"Body: {request.get_data(as_text=True)}")

    # Check if request is JSON
    if not request.is_json:
        return jsonify({"error": "Unsupported Media Type"}), 415

    data = request.get_json()
    
    # Check if request has necessary keys
    if "request" not in data or "type" not in data["request"]:
        return jsonify({"error": "Invalid Alexa request format"}), 400

    request_type = data["request"]["type"]

    # Handle LaunchRequest (when user opens the skill)
    if request_type == "LaunchRequest":
        return alexa_response("Halo! Saya siap membantu dengan Google Gemini.")

    # Handle IntentRequest (user asks something)
    elif request_type == "IntentRequest":
        intent_name = data["request"]["intent"]["name"]
        
        if intent_name == "AskGeminiIntent":
            user_question = data["request"]["intent"]["slots"]["query"]["value"]
            gemini_response = get_gemini_response(user_question)
            return alexa_response(gemini_response)

        else:
            return alexa_response("Saya tidak mengerti permintaan Anda.")

    # Handle SessionEndedRequest
    elif request_type == "SessionEndedRequest":
        return alexa_response("Sampai jumpa!")

    return alexa_response("Terjadi kesalahan saat memproses permintaan Anda.")

def alexa_response(text):
    """Format response for Alexa."""
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": text
            },
            "shouldEndSession": True
        }
    })

def get_gemini_response(user_question):
    """Call Google Gemini API to get response."""
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        return "API Key Google Gemini tidak ditemukan."

    import requests

    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateText"
    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": user_question,
        "temperature": 0.7,
        "max_tokens": 100
    }
    response = requests.post(f"{url}?key={API_KEY}", json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        return result.get("candidates", [{}])[0].get("output", "Saya tidak yakin dengan jawabannya.")
    else:
        return f"Error dari Google Gemini: {response.status_code}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
