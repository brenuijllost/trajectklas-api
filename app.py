@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("message")
    # Pak het model dat de website stuurt, of gebruik de standaard 'open-mistral-7b'
    chosen_model = data.get("model", "open-mistral-7b")
    
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": chosen_model, # Hier gebruiken we nu het gekozen model!
        "messages": [{"role": "user", "content": user_input}]
    }
    
    # ... de rest van je code blijft hetzelfde ...

Zodra je dit op GitHub opslaat, buildt Render hem opnieuw en kun je direct wisselen tussen modellen in je nieuwe interface! Let wel op: krachtigere modellen zoals `medium` kunnen iets langer duren om te antwoorden.
