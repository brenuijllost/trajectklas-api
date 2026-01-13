from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import os

# weetjenog: Initialiseer de Flask-app en sta Cross-Origin Resource Sharing toe
app = Flask(__name__)
CORS(app)

# weetjenog: Haal de API-key veilig op uit de omgevingsvariabelen van de server
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# weetjenog: De volledige HTML, CSS en JavaScript voor de gebruikersinterface
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trajectklas AI Chat</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* weetjenog: Zorg dat het chatvenster de juiste hoogte heeft op mobiel en desktop */
        .chat-container { height: calc(100vh - 180px); }
        .message-user { background-color: #3b82f6; color: white; border-radius: 18px 18px 2px 18px; align-self: flex-end; }
        .message-bot { background-color: #f3f4f6; color: #1f2937; border-radius: 18px 18px 18px 2px; align-self: flex-start; border: 1px solid #e5e7eb; }
        .markdown-text { white-space: pre-wrap; }
    </style>
</head>
<body class="bg-slate-50 font-sans leading-relaxed">
    <div class="max-w-4xl mx-auto bg-white shadow-2xl h-screen flex flex-col">
        
        <!-- weetjenog: Header van de applicatie -->
        <header class="bg-blue-700 p-5 text-white flex justify-between items-center shadow-lg">
            <div>
                <h1 class="text-2xl font-bold tracking-tight">Trajectklas AI</h1>
                <p class="text-xs text-blue-100 uppercase tracking-widest font-semibold">Educatieve Assistent</p>
            </div>
            <div class="flex items-center space-x-2">
                <span class="h-3 w-3 bg-green-400 rounded-full animate-pulse"></span>
                <span class="text-sm font-medium">Systeem Actief</span>
            </div>
        </header>

        <!-- weetjenog: Het gebied waar de berichten verschijnen -->
        <div id="chat-window" class="chat-container overflow-y-auto p-6 flex flex-col space-y-4 bg-white">
            <div class="message-bot p-4 max-w-[85%] shadow-sm">
                <p class="font-bold mb-1 text-blue-700">AI:</p>
                <p>Welkom bij de Trajectklas! Ik ben je persoonlijke assistent. Waar kan ik je vandaag bij ondersteunen?</p>
            </div>
        </div>

        <!-- weetjenog: Inputgedeelte onderaan het scherm -->
        <div class="p-4 border-t-2 border-slate-100 bg-white shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
            <div class="flex items-center space-x-3 max-w-4xl mx-auto">
                <input type="text" id="user-input" autocomplete="off"
                       placeholder="Stel je vraag aan de AI..." 
                       class="flex-1 border-2 border-slate-200 rounded-2xl px-5 py-3 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-lg">
                <button onclick="sendMessage()" id="send-btn" 
                        class="bg-blue-600 text-white p-3 rounded-2xl hover:bg-blue-700 active:scale-95 transition-all shadow-md">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                </button>
            </div>
            <p class="text-[10px] text-center mt-2 text-slate-400 font-medium">Aangedreven door Mistral AI - Veilig & Educatief</p>
        </div>
    </div>

    <script>
        const chatWindow = document.getElementById('chat-window');
        const userInput = document.getElementById('user-input');
        let history = [];

        // weetjenog: Functie om berichten visueel toe te voegen aan het scherm
        function addMessage(text, role) {
            const wrapper = document.createElement('div');
            wrapper.className = `flex w-full ${role === 'user' ? 'justify-end' : 'justify-start'}`;
            
            const div = document.createElement('div');
            div.className = `p-4 max-w-[85%] shadow-md transition-all duration-300 transform scale-100 markdown-text ${role === 'user' ? 'message-user' : 'message-bot'}`;
            
            const label = document.createElement('p');
            label.className = `text-[10px] font-bold mb-1 uppercase tracking-tighter ${role === 'user' ? 'text-blue-100' : 'text-blue-700'}`;
            label.textContent = role === 'user' ? 'Jij:' : 'AI:';
            
            const content = document.createElement('p');
            content.textContent = text;
            
            div.appendChild(label);
            div.appendChild(content);
            wrapper.appendChild(div);
            chatWindow.appendChild(wrapper);
            
            // weetjenog: Scroll automatisch naar het nieuwste bericht
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }

        // weetjenog: De hoofdfunctie die het bericht naar de Python backend stuurt
        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            addMessage(message, 'user');
            userInput.value = '';
            
            // weetjenog: Laat zien dat de AI bezig is
            const loadingId = "loading-" + Date.now();
            const loadingDiv = document.createElement('div');
            loadingDiv.id = loadingId;
            loadingDiv.className = "message-bot p-4 max-w-[85%] shadow-sm italic text-slate-400 animate-pulse";
            loadingDiv.textContent = "Bericht wordt verwerkt...";
            chatWindow.appendChild(loadingDiv);
            chatWindow.scrollTop = chatWindow.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        history: history,
                        model: "mistral-large-latest"
                    })
                });

                const data = await response.json();
                document.getElementById(loadingId).remove();

                if (data.choices && data.choices[0]) {
                    const botReply = data.choices[0].message.content;
                    addMessage(botReply, 'bot');
                    
                    // weetjenog: Onthoud het gesprek voor de context van de volgende vraag
                    history.push({ role: "user", content: message });
                    history.push({ role: "assistant", content: botReply });
                    
                    // weetjenog: Beperk geschiedenis om geheugen te besparen
                    if (history.length > 10) history = history.slice(-10);
                } else {
                    addMessage("Er is momenteel een storing in het systeem. Probeer het later nog eens.", 'bot');
                }
            } catch (error) {
                if(document.getElementById(loadingId)) document.getElementById(loadingId).remove();
                addMessage("Kan geen verbinding maken met de centrale server. Controleer je internet.", 'bot');
                console.error("Fout:", error);
            }
        }

        // weetjenog: Luister naar de 'Enter' toets om snel berichten te sturen
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    # weetjenog: Stuurt de complete webinterface naar de browser
    return render_template_string(HTML_INTERFACE)

@app.route('/chat', methods=['POST'])
def chat():
    # weetjenog: Verwerkt de inkomende chat-data en communiceert met Mistral AI
    data = request.get_json()
    if not data:
        return jsonify({"error": "Geen data ontvangen"}), 400

    user_input = data.get("message")
    chosen_model = data.get("model", "open-mistral-7b")
    history = data.get("history", [])

    # weetjenog: Bouw de berichtenlijst op voor de AI, beginnend met de historie
    messages = []
    for msg in history:
        messages.append({
            "role": msg.get("role"),
            "content": msg.get("content")
        })

    # weetjenog: Voeg de nieuwe vraag van de gebruiker toe
    if user_input:
        messages.append({
            "role": "user",
            "content": user_input
        })

    payload = {
        "model": chosen_model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # weetjenog: Verstuur het verzoek naar de officiële Mistral API
        response = requests.post("https://api.mistral.ai/v1/chat/completions", json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        # weetjenog: Log de fout en geef een nette melding terug aan de frontend
        print(f"API Fout: {e}")
        return jsonify({"error": "Fout bij communicatie met AI service"}), 500

if __name__ == '__main__':
    # weetjenog: Gebruik de poort die Render toewijst of standaard 5000
    port = int(os.environ.get("PORT", 5000))
    # weetjenog: Luister op 0.0.0.0 zodat de app van buitenaf bereikbaar is
    app.run(host='0.0.0.0', port=port, debug=False)
