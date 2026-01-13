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
    # Haal de historie op uit het verzoek
    history = data.get("history", [])

    # We bouwen de lijst met berichten op
    messages = []

    # 1. Voeg de bestaande geschiedenis toe aan de lijst
    for msg in history:
        # We voegen alleen tekstberichten uit de historie toe voor context
        messages.append({
            "role": msg.get("role"),
            "content": msg.get("content")
        })

    # 2. Maak de content voor het NIEUWE bericht (tekst + eventueel afbeelding)
    current_content = []
    if user_input:
        current_content.append({"type": "text", "text": user_input})
    
    if image_data:
        current_content.append({
            "type": "image_url",
            "image_url": image_data
        })

    # 3. Voeg het huidige bericht toe aan de berichtenlijst
    # Controleer of het bericht niet al per ongeluk in de history zat
    if current_content:
        messages.append({
            "role": "user",
            "content": current_content
        })

    # De payload die we naar Mistral sturen bevat nu alle eerdere berichten
    payload = {
        "model": chosen_model,
        "messages": messages
    }

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.mistral.ai/v1/chat/completions", json=payload, headers=headers)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Op Render gebruiken we meestal geen debug=True in productie, 
    # maar voor het testen is het prima.
    app.run(debug=True)
