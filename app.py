import os
import json
import base64
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests

# weetjenog:   Initialiseer de Flask-app en sta CORS toe voor flexibiliteit
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
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min. js"></script>
    <style>
        : :-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        . msg-user { background-color: #2563eb; color: white; border-radius: 18px 18px 2px 18px; }
        .msg-ai { background-color: white; color: #1e293b; border-radius: 18px 18px 18px 2px; border:  1px solid #e2e8f0; }
        . markdown-body pre { background: #0f172a; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; color: #f8fafc; }
        . markdown-body code { font-family: monospace; font-size: 0.9em; background: rgba(0,0,0,0.05); padding: 2px 4px; border-radius: 4px; }
    </style>
</head>
<body class="bg-slate-50 h-screen flex overflow-hidden font-sans text-slate-900">

    <!-- SIDEBAR:  Instellingen en Sliders -->
    <aside class="w-80 bg-white shadow-xl flex flex-col h-full border-r border-slate-200 hidden md:flex">
        <div class="p-6 border-b border-slate-100">
            <h1 class="text-xl font-bold text-blue-600">Trajectklas AI</h1>
            <p class="text-[10px] text-slate-400 uppercase font-bold tracking-widest italic">Configuratie Paneel</p>
        </div>
        
        <div class="p-6 space-y-6 flex-1 overflow-y-auto">
            <!-- Model Selectie -->
            <div>
                <label class="block text-xs font-bold text-blue-600 uppercase mb-2 tracking-wider">Model Selectie</label>
                <select id="model-select" class="w-full bg-slate-50 border border-slate-200 text-xs rounded-lg p-2.5 outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                    <optgroup label="🚀 FRONTIER (Meest Capabel)">
                        <option value="mistral-large-3-v25-12">Mistral Large 3 (v25.12)</option>
                        <option value="mistral-medium-3-1-premier-v25-08">Mistral Medium 3.1 (v25.08)</option>
                    </optgroup>
                    <optgroup label="📚 GENERALIST">
                        <option value="mistral-small-3-2-v25-06">Mistral Small 3.2 (v25.06)</option>
                        <option value="ministral-3-14b-v25-12">Ministral 3 14B (v25.12)</option>
                        <option value="ministral-3-8b-v25-12">Ministral 3 8B (v25.12)</option>
                        <option value="ministral-3-3b-v25-12">Ministral 3 3B (v25.12)</option>
                        <option value="magistral-medium-1-2-premier-v25-09">Magistral Medium 1.2 (v25.09)</option>
                        <option value="magistral-small-1-2-v25-09">Magistral Small 1.2 (v25.09)</option>
                    </optgroup>
                    <optgroup label="🔧 SPECIALIST">
                        <option value="ocr-3-premier-v25-12">OCR 3 (Document) (v25.12)</option>
                        <option value="codestral-premier-v25-08">Codestral (Code) (v25.08)</option>
                        <option value="codestral-embed-premier-v25-05">Codestral Embed (v25.05)</option>
                        <option value="devstral-2-v25-12">Devstral 2 (Code Agent) (v25.12)</option>
                        <option value="voxtral-mini-transcribe-v25-07">Voxtral Mini Transcribe (v25.07)</option>
                        <option value="voxtral-mini-v25-07">Voxtral Mini (Audio) (v25.07)</option>
                        <option value="voxtral-small-v25-07">Voxtral Small (Audio) (v25.07)</option>
                        <option value="mistral-moderation-premier-v24-11">Mistral Moderation (v24.11)</option>
                    </optgroup>
                    <optgroup label="⭐ OVERIGE">
                        <option value="devstral-small-2-labs-v25-12">Devstral Small 2 Labs (v25.12)</option>
                        <option value="mistral-medium-3-premier-v25-05">Mistral Medium 3 (v25.05)</option>
                        <option value="mistral-large-2-1-premier-v24-11">Mistral Large 2.1 (v24.11)</option>
                        <option value="pixtral-large-premier-v24-11">Pixtral Large (Vision) (v24.11)</option>
                        <option value="ocr-2-premier-v25-05">OCR 2 (v25.05)</option>
                        <option value="mistral-nemo-12b-2024-07">Mistral Nemo 12B (2024-07)</option>
                    </optgroup>
                </select>
            </div>
            
            <!-- Temperatuur Slider -->
            <div class="space-y-3">
                <div class="flex justify-between items-center">
                    <label class="text-xs font-bold text-slate-600 uppercase">Temperatuur</label>
                    <span id="val-temp" class="text-xs font-mono text-blue-600 font-bold">0. 7</span>
                </div>
                <input type="range" id="param-temp" min="0" max="1.5" step="0.1" value="0.7" 
                       class="w-full h-1. 5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                       oninput="document.getElementById('val-temp').innerText = this.value">
                <p class="text-[9px] text-slate-400 leading-tight">Hoe hoger, hoe creatiever en onvoorspelbaarder. </p>
            </div>

            <!-- Top P Slider -->
            <div class="space-y-3">
                <div class="flex justify-between items-center">
                    <label class="text-xs font-bold text-slate-600 uppercase">Top P</label>
                    <span id="val-topp" class="text-xs font-mono text-blue-600 font-bold">1.0</span>
                </div>
                <input type="range" id="param-topp" min="0" max="1" step="0.05" value="1" 
                       class="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                       oninput="document.getElementById('val-topp').innerText = this.value">
                <p class="text-[9px] text-slate-400 leading-tight">Nucleus sampling:  beperkt de woordkeuze tot de top waarschijnlijkheid.</p>
            </div>

            <!-- Max Tokens Slider -->
            <div class="space-y-3">
                <div class="flex justify-between items-center">
                    <label class="text-xs font-bold text-slate-600 uppercase">Max Lengte</label>
                    <span id="val-tokens" class="text-xs font-mono text-blue-600 font-bold">1500</span>
                </div>
                <input type="range" id="param-tokens" min="100" max="4000" step="100" value="1500" 
                       class="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                       oninput="document. getElementById('val-tokens').innerText = this.value">
                <p class="text-[9px] text-slate-400 leading-tight">Maximaal aantal tokens in het antwoord.</p>
            </div>
        </div>

        <div class="p-4 bg-slate-50 border-t border-slate-100 text-center space-y-2">
            <button onclick="window.location.reload()" class="w-full py-2 text-[10px] text-slate-400 font-bold hover:text-red-500 transition uppercase tracking-widest border border-slate-200 rounded">⟲ Vernieuwen</button>
            <p class="text-[9px] text-slate-300">Veilig & Educatief - Trajectklas v3.0</p>
        </div>
    </aside>

    <!-- HOOFDSCHERM: Chatvenster -->
    <main class="flex-1 flex flex-col h-full relative">
        <div id="chat-window" class="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 bg-slate-50">
            <div class="flex justify-start">
                <div class="msg-ai p-4 max-w-[85%] shadow-sm text-sm border border-slate-200">
                    <p class="font-bold mb-1 text-blue-600">AI Assistent: </p>
                    <p>Welkom terug! Alle modellen zijn nu met geldige API IDs geconfigureerd.  Hoe kan ik je vandaag ondersteunen?</p>
                </div>
            </div>
        </div>

        <!-- Preview voor geüploade bestanden -->
        <div id="upload-preview" class="px-6 py-3 bg-white border-t border-blue-100 hidden flex items-center gap-4">
            <div id="preview-box" class="w-10 h-10 rounded bg-slate-100 flex items-center justify-center overflow-hidden border border-slate-200 shadow-inner text-xs"></div>
            <p id="file-name" class="text-xs font-bold flex-1 truncate text-slate-600"></p>
            <button onclick="removeFile()" class="text-red-400 hover:text-red-600 transition"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></button>
        </div>

        <!-- Invoergebied onderaan -->
        <div class="p-4 md:p-6 bg-white border-t border-slate-200 shadow-[0_-4px_10px_rgba(0,0,0,0.03)]">
            <div class="max-w-4xl mx-auto flex gap-3 items-end">
                <input type="file" id="file-input" class="hidden" onchange="handleFile(event)">
                <button onclick="document.getElementById('file-input').click()" title="Bestand toevoegen" class="h-12 w-12 flex items-center justify-center rounded-xl bg-slate-100 text-slate-500 hover:bg-slate-200 transition">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                </button>
                <textarea id="user-input" rows="1" class="flex-1 p-3. 5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus: ring-blue-500 outline-none text-sm resize-none transition-all" placeholder="Typ je vraag hier..."></textarea>
                <button onclick="sendMessage()" id="send-btn" class="h-12 w-12 flex items-center justify-center rounded-xl bg-blue-600 text-white hover:bg-blue-700 transition shadow-lg shadow-blue-200">
                    <svg class="w-5 h-5 transform rotate-90" fill="currentColor" viewBox="0 0 20 20"><path d="M10. 894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15. 571V11a1 1 0 00-2 0v4.571L2.275 16.96a1 1 0 001.169 1.409l7-14z"/></svg>
                </button>
            </div>
        </div>
    </main>

    <script>
        let history = [];
        let selectedFile = null;

        marked.setOptions({ breaks: true, highlight: (code) => hljs.highlightAuto(code).value });

        function addMessage(text, role) {
            const div = document.createElement('div');
            div.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
            div.innerHTML = `
                <div class="${role === 'user' ? 'msg-user' : 'msg-ai'} p-4 shadow-sm text-sm max-w-[85%] border border-transparent ${role !== 'user' ? 'border-slate-200' : ''}">
                    <p class="text-[10px] font-bold mb-1 opacity-70 uppercase tracking-widest">${role === 'user' ? 'Jij' : 'AI'}</p>
                    <div class="markdown-body">${marked. parse(text)}</div>
                </div>`;
            document.getElementById('chat-window').appendChild(div);
            document.getElementById('chat-window').scrollTop = document. getElementById('chat-window').scrollHeight;
        }

        function handleFile(e) {
            selectedFile = e.target.files[0];
            if (! selectedFile) return;
            document.getElementById('upload-preview').classList.remove('hidden');
            document.getElementById('file-name').innerText = selectedFile.name;
            const previewBox = document.getElementById('preview-box');
            if(selectedFile.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(selectedFile);
                img. className = "w-full h-full object-cover rounded";
                previewBox.innerHTML = '';
                previewBox. appendChild(img);
            } else {
                previewBox.innerHTML = '📄';
            }
        }

        function removeFile() {
            selectedFile = null;
            document. getElementById('upload-preview').classList.add('hidden');
            document.getElementById('file-input').value = '';
        }

        async function sendMessage() {
            const textInput = document.getElementById('user-input');
            const message = textInput.value.trim();
            if (!message && ! selectedFile) return;

            const model = document.getElementById('model-select').value;
            const temp = document.getElementById('param-temp').value;
            const topp = document.getElementById('param-topp').value;
            const tokens = document.getElementById('param-tokens').value;

            addMessage(message || "Bestand geüpload voor analyse", 'user');
            textInput.value = '';
            
            const payload = {
                message: message,
                history: history,
                model: model,
                temp: temp,
                top_p: topp,
                max_tokens: tokens
            };

            if (selectedFile) {
                const reader = new FileReader();
                reader.onload = async () => {
                    payload.file_data = reader.result. split(',')[1];
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

            const loadingId = "loader-" + Date.now();
            const loader = document.createElement('div');
            loader.id = loadingId;
            loader.className = "text-[10px] text-slate-400 font-bold animate-pulse px-4";
            loader.innerText = "Systeem verwerkt verzoek met " + payload.model + "...";
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
                    history.push({role: "user", content: payload.message || "Bestand geanalyseerd"});
                    history.push({role: "assistant", content: data.reply});
                    if (history.length > 12) history = history.slice(-12);
                } else {
                    addMessage("Fout: " + (data.error || "De AI reageert niet correct. "), 'ai');
                }
            } catch (e) {
                if(document.getElementById(loadingId)) document.getElementById(loadingId).remove();
                addMessage("Verbindingsfout:  Kan de server niet bereiken.", 'ai');
            } finally {
                btn.disabled = false;
                btn.classList. remove('opacity-50');
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
    return render_template_string(HTML_INTERFACE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])
    model = data.get('model', 'mistral-large-3-v25-12')
    temp = float(data.get('temp', 0.7))
    top_p = float(data.get('top_p', 1.0))
    max_tokens = int(data.get('max_tokens', 1500))
    
    messages = []
    for h in history:
        messages.append({"role": h['role'], "content": h['content']})
    
    content = [{"type": "text", "text": user_message or "Analyseer dit bestand aub. "}]
    
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
        "top_p": top_p,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=45)
        response_data = response.json()
        
        if response.status_code == 200:
            reply = response_data['choices'][0]['message']['content']
            return jsonify({"reply": reply})
        else:
            error_msg = response_data.get('message', 'Onbekende API fout')
            return jsonify({"error": error_msg}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__': 
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
