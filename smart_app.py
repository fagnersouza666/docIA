from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from smart_indexer import SmartDocumentIndexer
import logging
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

indexer = SmartDocumentIndexer()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Busca Inteligente de Atas</title>
    <style>
        body { font-family: sans-serif; max-width: 1400px; margin: auto; padding: 20px; background: #f0f2f5; }
        .container { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .search-box { display: flex; gap: 15px; margin-bottom: 30px; }
        input[type="text"] { flex: 1; padding: 15px; font-size: 17px; border-radius: 25px; border: 2px solid #ddd; transition: border-color 0.3s; }
        input[type="text"]:focus { border-color: #007bff; outline: none; }
        button { padding: 15px 25px; font-size: 16px; border-radius: 25px; border: none; cursor: pointer; background: #007bff; color: white; transition: background 0.3s; }
        button:hover { background: #0056b3; }
        .stats { background: #e9ecef; padding: 20px; border-radius: 10px; margin-bottom: 30px; text-align: center; font-size: 16px; }
        .ai-answer { 
            background: linear-gradient(135deg, #e7f3ff 0%, #f0f8ff 100%); 
            border-left: 6px solid #007bff; 
            padding: 40px; 
            border-radius: 12px; 
            margin-top: 25px;
            min-height: 300px;
            max-height: 800px;
            overflow-y: auto;
            font-size: 17px;
            line-height: 1.8;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid #e3f2fd;
        }
        #results {
            min-height: 350px;
            padding: 20px;
            margin-top: 20px;
        }
        .loading, .no-results { 
            text-align: center; 
            padding: 60px; 
            color: #6c757d; 
            font-size: 18px;
            background: #f8f9fa;
            border-radius: 10px;
            border: 2px dashed #dee2e6;
        }
        .response-text {
            font-size: 17px;
            line-height: 1.8;
            margin-bottom: 20px;
            color: #2c3e50;
        }
        .confidence-info {
            font-size: 15px;
            color: #666;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid #e3f2fd;
            font-weight: 500;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            font-size: 28px;
        }
        h3 {
            color: #2c3e50;
            font-size: 20px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Busca Inteligente de Atas</h1>
        <div id="stats" class="stats">Carregando...</div>
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Faça uma pergunta sobre as atas...">
            <button onclick="search()">Buscar</button>
            <button onclick="reindexDocuments()">Reindexar</button>
        </div>
        <div id="results"></div>
    </div>
    <script>
        function search() {
            const query = document.getElementById('searchInput').value;
            const resultsDiv = document.getElementById('results');
            if (!query) return;
            resultsDiv.innerHTML = '<div class="loading">Buscando...</div>';
            fetch('/search', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({query}) })
                .then(res => res.json())
                .then(data => {
                    if (data.success && data.results.length > 0) {
                        const result = data.results[0];
                        let html = '<h3>Resposta:</h3>';
                        if (result.ai_answer) {
                            html += `<div class="ai-answer">
                                <div class="response-text"><b>Resposta IA:</b> ${result.ai_answer}</div>
                                <div class="confidence-info">Confiança: ${Math.round(result.confidence * 100)}%</div>
                            </div>`;
                        } else {
                            html += '<div class="ai-answer"><div class="response-text">Nenhuma resposta direta encontrada, mas o trecho a seguir pode ser útil.</div></div>';
                        }
                        resultsDiv.innerHTML = html;
                    } else {
                        resultsDiv.innerHTML = '<div class="no-results">Nenhum resultado encontrado.</div>';
                    }
                });
        }
        function reindexDocuments() {
            fetch('/index', { method: 'POST' }).then(() => { alert('Reindexação iniciada em background!'); loadStats(); });
        }
        function loadStats() {
            fetch('/stats').then(res => res.json()).then(data => {
                if (data.success) {
                    let modelInfo = '';
                    if (data.model_status.includes('Sistema Interno')) {
                        modelInfo = ` | Modelo: ${data.model_status} ⚠️ (Instale Ollama+Mistral para melhor qualidade)`;
                    } else {
                        modelInfo = ` | Modelo: ${data.model_status} ✅`;
                    }
                    document.getElementById('stats').innerText = `${data.total_documents} documentos indexados${modelInfo}`;
                }
            });
        }
        window.onload = loadStats;
    </script>
</body>
</html>
"""

class DocumentsEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if not event.is_directory and any(event.src_path.endswith(ext) for ext in ['.pdf', '.docx', '.txt']):
            logger.info(f"Alteração detectada em '{event.src_path}'. Reindexando em background...")
            threading.Thread(target=indexer.index_directory, args=("documents",), daemon=True).start()

def start_watcher():
    if os.path.exists("documents"):
        observer = Observer()
        observer.schedule(DocumentsEventHandler(), "documents", recursive=True)
        observer.daemon = True
        observer.start()
        logger.info("Monitoramento automático da pasta 'documents' ativado.")

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search_endpoint():
    query = request.json.get('query', '').strip()
    if not query: return jsonify({'success': False, 'error': 'Query vazia'})
    results = indexer.search(query, max_results=1)
    return jsonify({'success': True, 'results': results})

@app.route('/index', methods=['POST'])
def index_documents_endpoint():
    threading.Thread(target=indexer.index_directory, args=("documents",), daemon=True).start()
    return jsonify({'success': True, 'message': 'Reindexação iniciada em background.'})

@app.route('/stats')
def stats_endpoint():
    stats_data = indexer.get_stats()
    return jsonify({'success': True, **stats_data})

if __name__ == '__main__':
    if not os.path.exists("documents"): os.makedirs("documents")
    indexer.index_directory("documents")
    start_watcher()
    app.run(host='0.0.0.0', port=5000)
