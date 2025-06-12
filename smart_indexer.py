import os
import json
from datetime import datetime
import PyPDF2
from docx import Document
import logging
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings

warnings.filterwarnings("ignore")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartDocumentIndexer:
    def __init__(self):
        self.documents = []
        self.index_file = "smart_documents_index.json"
        self.last_update = None
        self.vectorizer = TfidfVectorizer(
            stop_words=self._get_portuguese_stop_words(),
            max_features=5000,
            ngram_range=(1, 3)
        )
        self.document_vectors = None
        self.qa_pipeline = None
        self._init_qa_model()
        self.load_index()

    def _init_qa_model(self):
        """Inicializa modelo de linguagem generativo para respostas naturais"""
        try:
            logger.info("Inicializando modelo de linguagem generativo...")
            # Tentar usar Ollama local com preferência pelo modelo Mistral
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                models = []
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    names = [m.get('name', '').lower() for m in models]
                    if not any('mistral' in n for n in names):
                        try:
                            pull_resp = requests.post(
                                "http://localhost:11434/api/pull",
                                json={"model": "mistral", "stream": False},
                                timeout=30
                            )
                            if pull_resp.status_code == 200:
                                logger.info("Modelo Mistral baixado via Ollama")
                                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                                if response.status_code == 200:
                                    models = response.json().get('models', [])
                        except Exception as e:
                            logger.error(f"Erro ao baixar modelo no Ollama: {e}")
                if models:
                    self.llm_type = "ollama"
                    self.model_name = None
                    for m in models:
                        name = m.get('name', '').lower()
                        if 'mistral' in name:
                            self.model_name = m['name']
                            break
                    if not self.model_name:
                        self.model_name = models[0]['name']
                    logger.info(f"✅ Ollama detectado com modelo: {self.model_name}")
                    return
            except Exception as e:
                logger.error(f"Erro ao verificar Ollama: {e}")
            # Fallback para Hugging Face
            try:
                from transformers import pipeline
                import torch
                device = 0 if torch.cuda.is_available() else -1
                self.qa_pipeline = pipeline(
                    "text-generation",
                    model="mistralai/Mistral-7B-Instruct-v0.2",
                    device=device
                )
                self.llm_type = "huggingface"
                logger.info("✅ Modelo Hugging Face Mistral-7B carregado")
                return
            except Exception as e:
                logger.error(f"Erro ao carregar modelo Hugging Face: {e}")
            logger.warning("Usando modo de resposta baseado em contexto (fallback)")
            self.qa_pipeline = None
            self.llm_type = "simple"
        except Exception as e:
            logger.error(f"Erro ao inicializar modelo generativo: {e}")
            self.qa_pipeline = None
            self.llm_type = "simple"

    def index_directory(self, directory_path):
        """Indexa todos os documentos de um diretório"""
        logger.info(f"Iniciando indexação do diretório: {directory_path}")
        self.documents = []
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            content = ""
            if filename.endswith(".pdf"):
                content = self._read_pdf(file_path)
            elif filename.endswith(".docx"):
                content = self._read_docx(file_path)
            elif filename.endswith(".txt"):
                content = self._read_txt(file_path)
            
            if content:
                doc_id = len(self.documents) + 1
                chunks = self._chunk_text(content)
                doc = {
                    'id': doc_id, 'filename': filename, 'content': content, 
                    'chunks': chunks, 'file_path': file_path, 'indexed_at': datetime.now().isoformat()
                }
                self.documents.append(doc)
        if self.documents:
            self._vectorize_documents()
        self.save_index()
        self.last_update = datetime.now().isoformat()
        logger.info(f"Indexação concluída. {len(self.documents)} documentos processados.")

    def _chunk_text(self, text, chunk_size=1000, overlap=200):
        """Divide o texto em chunks com sobreposição"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def _vectorize_documents(self):
        """Cria vetores TF-IDF para todos os chunks de documentos"""
        all_chunks = [chunk for doc in self.documents for chunk in doc.get('chunks', [doc['content']])]
        if all_chunks:
            self.document_vectors = self.vectorizer.fit_transform(all_chunks)
            logger.info(f"Vetorização concluída: {self.document_vectors.shape[0]} chunks vetorizados.")

    def save_index(self):
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=4)

    def load_index(self):
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            if self.documents:
                self.last_update = max(d.get("indexed_at") for d in self.documents)
                self._vectorize_documents()
            logger.info(f"Índice carregado: {len(self.documents)} documentos.")

    def _semantic_search(self, query, max_results=5):
        """Realiza busca semântica usando TF-IDF e similaridade de cosseno"""
        if not self.documents or self.document_vectors is None: return []
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.document_vectors)[0]
        chunk_similarities = sorted([(similarities[i], i) for i in range(len(similarities)) if similarities[i] > 0.01], reverse=True)
        results, added_docs, chunk_to_doc_map = [], set(), {}
        chunk_idx = 0
        for doc in self.documents:
            for chunk in doc.get('chunks', [doc['content']]):
                chunk_to_doc_map[chunk_idx] = (doc, chunk)
                chunk_idx += 1
        for similarity, idx in chunk_similarities[:max_results * 2]:
            if idx in chunk_to_doc_map:
                doc, chunk = chunk_to_doc_map[idx]
                if doc['id'] not in added_docs:
                    results.append({'id': doc['id'], 'filename': doc['filename'], 'content': doc['content'], 'relevant_chunk': chunk, 'similarity_score': float(similarity)})
                    added_docs.add(doc['id'])
                    if len(results) >= max_results: break
        return sorted(results, key=lambda x: x['similarity_score'], reverse=True)

    def search(self, query, max_results=10):
        """Realiza busca inteligente com compreensão de linguagem natural"""
        semantic_results = self._semantic_search(query, max_results)
        if not semantic_results: return []
        enhanced_results = []
        for result in semantic_results:
            enhanced_result = result.copy()
            context_chunks = [result['relevant_chunk']]
            answer = self._answer_question(query, context_chunks)
            if answer:
                enhanced_result['ai_answer'] = answer['answer']
                enhanced_result['confidence'] = answer['confidence']
            else:
                enhanced_result['ai_answer'] = f"Baseado no documento '{result['filename']}', o trecho mais relevante menciona: {result['relevant_chunk'][:300]}..."
                enhanced_result['confidence'] = 0.5
            enhanced_results.append(enhanced_result)
        return enhanced_results

    def _answer_question(self, question, context_chunks):
        context = " ".join(context_chunks)[:2000]
        if hasattr(self, 'llm_type'):
            if self.llm_type == "ollama": return self._answer_with_ollama(question, context)
            if self.llm_type == "huggingface": return self._answer_with_huggingface(question, context)
        return self._generate_natural_answer(question, context)

    def _answer_with_ollama(self, question, context):
        """Resposta usando Ollama local"""
        try:
            import requests
            prompt = f"""Você é um assistente de atas de reunião. Responda APENAS com a informação solicitada, de forma curta, direta e natural, em português. Se não souber, diga: 'Não encontrei essa informação nas atas.'
CONTEXTO: {context}
PERGUNTA: {question}
RESPOSTA:"""
            response = requests.post("http://localhost:11434/api/generate", json={"model": self.model_name, "prompt": prompt, "stream": False, "options": {"temperature": 0.2, "num_predict": 100}}, timeout=30)
            if response.status_code == 200:
                answer = response.json().get('response', '').strip()
                if answer: return {'answer': answer, 'confidence': 0.95}
        except Exception as e: logger.error(f"Erro no Ollama: {e}")
        return None

    def _answer_with_huggingface(self, question, context):
        """Resposta usando Hugging Face"""
        try:
            prompt = f"Responda APENAS com a informação solicitada, curta, direta e natural, em português. Se não souber, diga: 'Não encontrei essa informação nas atas.'\n\nContexto: {context}\n\nPergunta: {question}\nResposta:"
            result = self.qa_pipeline(prompt, max_length=len(prompt) + 80, num_return_sequences=1, temperature=0.2, pad_token_id=50256)
            if result and result[0]['generated_text']:
                answer = result[0]['generated_text'][len(prompt):].strip()
                if answer: return {'answer': answer, 'confidence': 0.9}
        except Exception as e: logger.error(f"Erro no Hugging Face: {e}")
        return None

    def _generate_natural_answer(self, question, context):
        """Gera resposta natural baseada no contexto (fallback)"""
        q_lower, c_lower = question.lower(), context.lower()
        if 'quando' in q_lower:
            dates = re.findall(r'\d{2}/\d{2}/\d{4}', context)
            if dates: return {'answer': dates[0], 'confidence': 0.85}
        if 'quem' in q_lower:
            nomes = re.findall(r'([A-Z][a-z]+ [A-Z][a-z]+)', context)
            if nomes: return {'answer': nomes[0], 'confidence': 0.85}
        if any(term in q_lower for term in ['orçamento', 'valor']):
            money = re.findall(r'R\$\s*[\d.,]+', context)
            if money: return {'answer': money[0], 'confidence': 0.85}
        return {'answer': "Não encontrei essa informação nas atas.", 'confidence': 0.5}

    def _read_pdf(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return "".join((page.extract_text() or "") for page in reader.pages)
        except Exception as e: logger.error(f"Erro ao ler PDF {file_path}: {e}"); return ""

    def _read_docx(self, file_path):
        try:
            doc = Document(file_path)
            return "\n".join(para.text for para in doc.paragraphs)
        except Exception as e: logger.error(f"Erro ao ler DOCX {file_path}: {e}"); return ""

    def _read_txt(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f: return f.read()
        except Exception as e: logger.error(f"Erro ao ler TXT {file_path}: {e}"); return ""
        
    def _get_portuguese_stop_words(self):
        return ["a", "o", "as", "os", "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas", "com", "por", "para", "e", "ou", "mas", "se", "que", "qual", "quando", "como", "onde", "quem", "um", "uma", "uns", "umas"]
        
    def get_stats(self):
        return {
            'total_documents': len(self.documents),
            'last_update': self.last_update,
            'has_ai_model': self.qa_pipeline is not None or getattr(self, 'llm_type', '') == 'ollama'
        }
