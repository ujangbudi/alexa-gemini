import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Ambil API Key dari Environment Variable
GOOGLE_GEMINI_API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Google Gemini API for Alexa is running!"

@app.route("/chatgpt", methods=["POST"])
def chat_with_gemini():
    data = request.json
    user_input = data.get("text", "")

    # Format request ke Google Gemini API
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GOOGLE_GEMINI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": f"Jawab dalam Bahasa Indonesia: {user_input}"}]}]
    }

    response = requests.post(url, headers=headers, params=params, json=payload)
    
    if response.status_code == 200:
        answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        answer = "Maaf, saya tidak dapat menjawab saat ini."

    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)