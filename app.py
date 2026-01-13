@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("message")
    chosen_model = data.get("model", "open-mistral-7b")
    image_data = data.get("image") # De base64 string van de website

    content = []
    if user_input:
        content.append({"type": "text", "text": user_input})
    
    if image_data:
        # Mistral verwacht de afbeelding in dit formaat
        content.append({
            "type": "image_url",
            "image_url": image_data # Bevat data:image/jpeg;base64,...
        })

    payload = {
        "model": chosen_model,
        "messages": [{"role": "user", "content": content}]
    }
    
    # ... de rest van je requests.post blijft hetzelfde ...

**Wat er nu gebeurt:**
1.  Je selecteert **Pixtral** bovenaan.
2.  Je klikt op de **+** en kiest een foto.
3.  Je typt een vraag (bijv: "Wat zie je op deze foto?").
4.  De website maakt er een pakketje van en stuurt het naar Render, die het doorgeeft aan Mistral.

Super cool om dit in je eigen trajectklas-app te hebben! Laat je het weten als het uploaden lukt?
