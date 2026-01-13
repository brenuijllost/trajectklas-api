import os
import json
import base64
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests

# weetjenog: Initialiseer de Flask-app en sta CORS toe voor flexibiliteit
app = Flask(__name__)
CORS(app)

# --- CONFIGURATIE ---
# weetjenog: Haal de API-key veilig op uit de omgevingsvariabelen van de server (Render)
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# weetjenog: De geavanceerde HTML interface met werkende sliders en zijbalk
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trajectklas AI - Geavanceerd</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        .msg-user { background-color: #2563eb; color: white; border-radius: 18px 18px 2px 18px; }
        .msg-ai { background-color: white; color: #1e293b; border-radius: 18px 18px 18px 2px; border: 1px solid #e2e8f0; }
        .markdown-body pre { background: #0f172a; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; color: #f8fafc; }
        .markdown-body code { font-family: monospace; font-size: 0.9em; background: rgba(0,0,0,0.05); padding: 2px 4px; border-radius: 4px; }
    </style>
</head>
<body class="bg-slate-50 h-screen flex overflow-hidden font-sans">

    <!-- SIDEBAR: Instellingen en Sliders -->
    <aside class="w-72 bg-white shadow-xl flex flex-col h-full border-r border-slate-200 hidden md:flex">
        <div class="p-6 border-b border-slate-100">
            <h1 class="text-xl font-bold text-blue-600">Trajectklas AI</h1>
            <p class="text-[10px] text-slate-400 uppercase font-bold tracking-widest italic font-semibold">Instellingen</p>
        </div>
        <div class="p-6 space-y-6 flex-1 overflow-y-auto">
            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-2 text-blue-600 tracking-wider">Model Selectie</label>
                <select id="model-select" class="w-full bg-white border border-slate-300 text-sm rounded-lg p-2.5 outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                    <optgroup label="Krachtig">
                        <option value="mistral-large-latest" selected>Mistral Large 3</option>
                        <option value="mistral-medium-latest">Mistral Medium</option>
                    </optgroup>
                    <optgroup label="Snel / Licht">
                        <option value="mistral-small-latest">Mistral Small</option>
                        <option value="open-mistral-7b">Mistral 7B (v0.3)</option>
                    </optgroup>
                    <optgroup label="Specialistisch">
                        <option value="pixtral-12b-latest">Pixtral (Vision)</option>
                        <option value="codestral-latest">Codestral</option>
                    </optgroup>
                </select>
            </div>
            
            <!-- weetjenog: Werkende temperatuur slider -->
            <div class="space-y-4">
                <div class="flex justify-between items-center">
                    <label class="text-xs font-bold text-slate-600 uppercase">Creativiteit</label>
                    <span id="val-temp" class="text-xs font-mono text-blue-600 font-bold">0.7</span>
                </div>
                <input type="range" id="param-temp" min="0" max="1" step="0.1" value="0.7" 
                       class="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                       oninput="document.getElementById('val-temp').innerText = this.value">
                <p class="text-[9px] text-slate-400 leading-tight">Lager is feitelijker, hoger is creatiever.</p>
            </div>
        </div>
        <div class="p-4 bg-slate-50 border-t border-slate-100 text-center">
            <button onclick="window.location.reload()" class="text-[10px] text-slate-400 font-bold hover:text-red-500 transition uppercase tracking-widest">Gesprek Wissen</button>
        </div>
    </aside>

    <!-- HOOFDSCHERM: Chatvenster -->
    <main class="flex-1 flex flex-col h-full relative">
        <div id="chat-window" class="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 bg-slate-50">
            <div class="flex justify-start">
                <div class="msg-ai p-4 max-w-[85%] shadow-sm text-sm border border-slate-200">
                    <p class="font-bold mb-1 text-blue-600">AI Assistent:</p>
                    <p>Hallo! Ik ben klaar om je te helpen. Je kunt tekst sturen, vragen stellen of zelfs een afbeelding uploaden als je een vision-model selecteert.</p>
                </div>
            </div>
        </div>

        <!-- weetjenog: Preview voor geüploade bestanden -->
        <div id="upload-preview" class="px-6 py-3 bg-white border-t border-blue-100 hidden flex items-center gap-4">
            <div id="preview-box" class="w-10 h-10 rounded bg-slate-100 flex items-center justify-center overflow-hidden border border-slate-200 shadow-inner text-xs"></div>
            <p id="file-name" class="text-xs font-bold flex-1 truncate text-slate-600"></p>
            <button onclick="removeFile()" class="text-red-400 hover:text-red-600 transition"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12" stroke-width="2"/></svg></button>
        </div>

        <!-- weetjenog: Invoergebied onderaan -->
        <div class="p-4 md:p-6 bg-white border-t border-slate-200 shadow-[0_-4px_10px_rgba(0,0,0,0.03)]">
            <div class="max-w-4xl mx-auto flex gap-3 items-end">
                <input type="file" id="file-input" class="hidden" onchange="handleFile(event)">
                <button onclick="document.getElementById('file-input').click()" class="h-12 w-12 flex items-center justify-center rounded-xl bg-slate-100 text-slate-500 hover:bg-blue-50 hover:text-blue-600 transition border border-slate-200">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                </button>
                <textarea id="user-input" rows="1" class="flex-1 p-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm resize-none transition-all" placeholder="Typ je bericht..."></textarea>
                <button onclick="sendMessage()" id="send-btn" class="h-12 w-12 flex items-center justify-center rounded-xl bg-blue-600 text-white hover:bg-blue-700 transition shadow-lg shadow-blue-200">
                    <svg class="w-5 h-5 transform rotate-90" fill="currentColor" viewBox="0 0 20 20"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"/></svg>
                </button>
            </div>
        </div>
    </main>

    <script>
        let history = [];
        let selectedFile = null;

        // weetjenog: Configureer Markdown-parser
        marked.setOptions({ breaks: true, highlight: (code) => hljs.highlightAuto(code).value });

        function addMessage(text, role) {
            const div = document.createElement('div');
            div.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
            div.innerHTML = `
                <div class="${role === 'user' ? 'msg-user' : 'msg-ai'} p-4 shadow-sm text-sm max-w-[85%] border border-transparent ${role !== 'user' ? 'border-slate-200' : ''}">
                    <p class="text-[10px] font-bold mb-1 opacity-70 uppercase tracking-widest">${role === 'user' ? 'Jij' : 'AI'}</p>
                    <div class="markdown-body">${marked.parse(text)}</div>
                </div>`;
            document.getElementById('chat-window').appendChild(div);
            document.getElementById('chat-window').scrollTop = document.getElementById('chat-window').scrollHeight;
        }

        function handleFile(e) {
            selectedFile = e.target.files[0];
            if (!selectedFile) return;
            document.getElementById('upload-preview').classList.remove('hidden');
            document.getElementById('file-name').innerText = selectedFile.name;
            const previewBox = document.getElementById('preview-box');
            if(selectedFile.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(selectedFile);
                img.className = "w-full h-full object-cover rounded";
                previewBox.innerHTML = '';
                previewBox.appendChild(img);
            } else {
                previewBox.innerHTML = '📄';
            }
        }

        function removeFile() {
            selectedFile = null;
            document.getElementById('upload-preview').classList.add('hidden');
            document.getElementById('file-input').value = '';
        }

        async function sendMessage() {
            const textInput = document.getElementById('user-input');
            const message = textInput.value.trim();
            if (!message && !selectedFile) return;

            // Haal de waarden van de sliders en select op
            const model = document.getElementById('model-select').value;
            const temperature = document.getElementById('param-temp').value;

            addMessage(message || "Bestand geüpload", 'user');
            textInput.value = '';
            
            const payload = {
                message: message,
                history: history,
                model: model,
                temp: temperature
            };

            // weetjenog: Verwerk bestand indien aanwezig
            if (selectedFile) {
                const reader = new FileReader();
                reader.onload = async () => {
                    payload.file_data = reader.result.split(',')[1];
                    payload.file_type = selectedFile.type;
                    sendToBackend(payload);
                };
                reader.readAsDataURL(selectedFile);
            } else {
                sendToBackend(payload);
            }
        }

        async function sendToBackend(payload) {
            const btn = document.getElementById('send-btn');
            btn.disabled = true;
            btn.classList.add('opacity-50');

            // Laad-indicator
            const loadingId = "loader-" + Date.now();
            const loader = document.createElement('div');
            loader.id = loadingId;
            loader.className = "text-[10px] text-slate-400 font-bold animate-pulse px-4";
            loader.innerText = "Systeem verwerkt verzoek...";
            document.getElementById('chat-window').appendChild(loader);

            try {
                const resp = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await resp.json();
                
                document.getElementById(loadingId).remove();

                if (data.reply) {
                    addMessage(data.reply, 'ai');
                    history.push({role: "user", content: payload.message || "Bestand geüpload"});
                    history.push({role: "assistant", content: data.reply});
                    if (history.length > 12) history = history.slice(-12);
                } else {
                    addMessage("Er ging iets mis: " + (data.error || "Onbekende fout"), 'ai');
                }
            } catch (e) {
                document.getElementById(loadingId).remove();
                addMessage("Verbindingsfout met de server.", 'ai');
            } finally {
                btn.disabled = false;
                btn.classList.remove('opacity-50');
                removeFile();
            }
        }

        document.getElementById('user-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # weetjenog: Stuurt de complete geavanceerde interface naar de browser
    return render_template_string(HTML_INTERFACE)

@app.route('/chat', methods=['POST'])
def chat():
    # weetjenog: Verwerkt de inkomende chat-data incl. slider waarden
    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])
    model = data.get('model', 'mistral-large-latest')
    temp = float(data.get('temp', 0.7))
    
    # Berichtenlijst opbouwen vanuit historie
    messages = []
    for h in history:
        messages.append({"role": h['role'], "content": h['content']})
    
    # Nieuwe content bouwen (tekst + eventueel afbeelding)
    content = [{"type": "text", "text": user_message or "Analyseer dit bestand"}]
    
    # weetjenog: Ondersteuning voor vision (afbeeldingen)
    if data.get('file_data') and data.get('file_type', '').startswith('image/'):
        content.append({
            "type": "image_url",
            "image_url": f"data:{data['file_type']};base64,{data['file_data']}"
        })
    
    messages.append({"role": "user", "content": content})

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temp,
        "max_tokens": 1500
    }

    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=45)
        response_data = response.json()
        
        if response.status_code == 200:
            reply = response_data['choices'][0]['message']['content']
            return jsonify({"reply": reply})
        else:
            # Foutmelding van Mistral API doorsturen naar frontend
            error_msg = response_data.get('message', 'Onbekende API fout')
            return jsonify({"error": error_msg}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# weetjenog: Start de server op de poort die Render toewijst
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
