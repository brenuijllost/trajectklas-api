import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app) # Cruciaal voor je website!

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("message")
    
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "open-mistral-7b",
        "messages": [{"role": "user", "content": user_input}]
    }
    
    response = requests.post("https://api.mistral.ai/v1/chat/completions", json=payload, headers=headers)
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
