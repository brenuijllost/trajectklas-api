from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("message")
    chosen_model = data.get("model", "open-mistral-7b")
    image_data = data.get("image")

    content = []
    if user_input:
        content.append({"type": "text", "text": user_input})
    
    if image_data:
        content.append({
            "type": "image_url",
            "image_url": image_data
        })

    payload = {
        "model": chosen_model,
        "messages": [{"role": "user", "content": content}]
    }

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.mistral.ai/v1/chat/completions", json=payload, headers=headers)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)
