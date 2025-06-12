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
import string

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
        """Inicializa modelo de IA externo (prioriza Ollama)"""
        try:
            logger.info("Tentando conectar com modelo Ollama...")
            import requests
            
            # Tenta conectar com Ollama
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.llm_type = "ollama"
                
                # Usa modelo definido na variável de ambiente ou força Mistral como padrão
                model_env = os.getenv("OLLAMA_MODEL", "mistral")
                if model_env:
                    self.model_name = model_env
                elif models:
                    # Procura especificamente por Mistral nos modelos disponíveis
                    mistral_models = [m['name'] for m in models if 'mistral' in m['name'].lower()]
                    if mistral_models:
                        self.model_name = mistral_models[0]
                    else:
                        self.model_name = models[0]['name']
                else:
                    self.model_name = "mistral"  # sempre Mistral como padrão
                
                logger.info(f"✅ Ollama conectado com modelo: {self.model_name}")
                return
            
            logger.warning("Ollama não encontrado, tentando outros modelos...")
            
            # Se não conseguiu Ollama, tenta outros modelos
            try:
                from transformers import pipeline
                self.qa_pipeline = pipeline("text-generation", model="microsoft/DialoGPT-medium")
                self.llm_type = "huggingface"
                logger.info("✅ Modelo Hugging Face carregado")
                return
            except Exception as e:
                logger.warning(f"Hugging Face não disponível: {e}")
            
            # Fallback para sistema interno apenas se nada funcionar
            self.llm_type = "internal"
            self.qa_pipeline = None
            logger.warning("⚠️ Usando sistema interno - instale Ollama para melhor qualidade")
            
        except Exception as e:
            logger.warning(f"Erro ao conectar modelos IA: {e}")
            self.qa_pipeline = None
            self.llm_type = "internal"

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

    def _chunk_text(self, text, chunk_size=2000, overlap=400):
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
        if not semantic_results: 
            return [{'ai_answer': 'Não encontrei informações relacionadas à sua pergunta.', 'confidence': 0.1}]
        
        enhanced_results = []
        for result in semantic_results:
            enhanced_result = result.copy()
            # Usa múltiplos chunks para contexto mais rico
            context_chunks = [result['relevant_chunk']]
            
            # Adiciona chunks adjacentes do mesmo documento para mais contexto
            if len(semantic_results) > 1:
                for other_result in semantic_results[1:3]:  # Adiciona até 2 chunks extras
                    if other_result['id'] == result['id']:  # Mesmo documento
                        context_chunks.append(other_result['relevant_chunk'])
            
            # PRIORIZA SEMPRE O MODELO DE IA (Mistral/Ollama)
            combined_context = " ".join(context_chunks)
            answer = self._answer_question(query, [combined_context])
            
            if answer:
                enhanced_result['ai_answer'] = answer['answer']
                enhanced_result['confidence'] = answer['confidence']
            else:
                # Só usa sistema interno se o modelo de IA falhar
                fallback_answer = self._generate_natural_answer(query, combined_context)
                enhanced_result['ai_answer'] = fallback_answer['answer']
                enhanced_result['confidence'] = fallback_answer['confidence']
            
            enhanced_results.append(enhanced_result)
        return enhanced_results

    def _answer_question(self, question, context_chunks):
        context = " ".join(context_chunks)[:3000]  # Aumenta o contexto para 3000 caracteres
        
        # SEMPRE TENTA OLLAMA/MISTRAL PRIMEIRO
        ollama_answer = self._answer_with_ollama(question, context)
        if ollama_answer:
            return ollama_answer
        
        # Se Ollama falhar, tenta Hugging Face
        if hasattr(self, 'llm_type') and self.llm_type == "huggingface":
            hf_answer = self._answer_with_huggingface(question, context)
            if hf_answer:
                return hf_answer
        
        # Retorna None para usar o sistema interno como fallback
        return None

    def _answer_with_ollama(self, question, context):
        """Resposta usando Ollama/Mistral"""
        try:
            import requests
            
            # Detecta automaticamente o modelo disponível se não estiver definido
            if not hasattr(self, 'model_name'):
                try:
                    models_response = requests.get("http://localhost:11434/api/tags", timeout=2)
                    if models_response.status_code == 200:
                        models = models_response.json().get('models', [])
                        self.model_name = models[0]['name'] if models else "mistral"
                    else:
                        self.model_name = "mistral"
                except:
                    self.model_name = "mistral"
            
            prompt = f"""Responda de forma natural e direta em português, baseado apenas no contexto fornecido. Se não encontrar a informação, diga que não encontrou.

CONTEXTO: {context}

PERGUNTA: {question}

RESPOSTA:"""

            response = requests.post(
                "http://localhost:11434/api/generate", 
                json={
                    "model": self.model_name, 
                    "prompt": prompt, 
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 200,
                        "top_p": 0.9
                    }
                }, 
                timeout=30
            )
            
            if response.status_code == 200:
                answer = response.json().get('response', '').strip()
                if answer and len(answer) > 10:  # Garante resposta mínima
                    return {'answer': answer, 'confidence': 0.95}
                    
        except Exception as e:
            logger.error(f"Erro no Ollama: {e}")
        
        return None

    def _answer_with_huggingface(self, question, context):
        """Resposta usando Hugging Face"""
        try:
            prompt = f"Responda APENAS com a informação solicitada, curta, direta e natural, em português. Se não souber, diga: 'Não encontrei essa informação.'\n\nContexto: {context}\n\nPergunta: {question}\nResposta:"
            result = self.qa_pipeline(prompt, max_length=len(prompt) + 80, num_return_sequences=1, temperature=0.2, pad_token_id=50256)
            if result and result[0]['generated_text']:
                answer = result[0]['generated_text'][len(prompt):].strip()
                if answer: return {'answer': answer, 'confidence': 0.9}
        except Exception as e: logger.error(f"Erro no Hugging Face: {e}")
        return None

    def _generate_natural_answer(self, question, context):
        """Gera resposta natural baseada no contexto (sistema interno inteligente)"""
        if not context or not context.strip():
            return {'answer': "Não encontrei informações relacionadas à sua pergunta.", 'confidence': 0.1}
            
        q_lower, c_lower = question.lower(), context.lower()
        
        # Busca por datas
        if any(term in q_lower for term in ['quando', 'data', 'dia', 'período']):
            dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', context)
            if dates:
                # Busca contexto adicional sobre a data
                sentences_with_date = [s.strip() for s in context.split('.') if dates[0] in s and len(s.strip()) > 10]
                if sentences_with_date:
                    extended_context = sentences_with_date[0]
                    if len(extended_context) > 300:
                        extended_context = extended_context[:300] + "..."
                    return {'answer': f"Isso ocorreu em {dates[0]}. {extended_context}", 'confidence': 0.85}
                return {'answer': f"Isso ocorreu em {dates[0]}.", 'confidence': 0.85}
            # Busca por meses/anos
            months = re.findall(r'(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)', c_lower)
            years = re.findall(r'20\d{2}', context)
            if months and years:
                return {'answer': f"Isso aconteceu em {months[0]} de {years[0]}.", 'confidence': 0.8}
        
        # Busca por pessoas
        if any(term in q_lower for term in ['quem', 'pessoa', 'responsável', 'diretor', 'presidente']):
            nomes = re.findall(r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', context)
            if nomes:
                # Busca contexto sobre a pessoa
                person_context = []
                for sentence in context.split('.'):
                    if any(nome in sentence for nome in nomes[:3]) and len(sentence.strip()) > 15:
                        person_context.append(sentence.strip())
                
                if person_context:
                    full_context = '. '.join(person_context[:2])
                    if len(full_context) > 400:
                        full_context = full_context[:400] + "..."
                    return {'answer': f"{nomes[0]} está relacionado a esta questão. {full_context}", 'confidence': 0.85}
                return {'answer': f"{nomes[0]} está relacionado a esta questão.", 'confidence': 0.85}
        
        # Busca por valores monetários
        if any(term in q_lower for term in ['orçamento', 'valor', 'custo', 'preço', 'real', 'reais', 'investimento']):
            money = re.findall(r'R\$\s*[\d.,]+', context)
            if money:
                # Busca contexto sobre o valor
                money_context = []
                for sentence in context.split('.'):
                    if any(valor in sentence for valor in money) and len(sentence.strip()) > 15:
                        money_context.append(sentence.strip())
                
                if money_context:
                    full_context = '. '.join(money_context[:2])
                    if len(full_context) > 350:
                        full_context = full_context[:350] + "..."
                    return {'answer': f"O valor mencionado é de {money[0]}.", 'confidence': 0.85}
                return {'answer': f"O valor mencionado é de {money[0]}.", 'confidence': 0.85}
        
        # Busca por status/situação
        if any(term in q_lower for term in ['como', 'situação', 'status', 'estado']):
            sentences = [s.strip() for s in context.split('.') if s.strip()]
            relevant_sentences = []
            for sentence in sentences[:5]:  # Analisa as 5 primeiras frases
                if any(word in sentence.lower() for word in q_lower.split() if len(word) > 3):
                    relevant_sentences.append(sentence)
            
            if relevant_sentences:
                full_answer = '. '.join(relevant_sentences[:3])
                if len(full_answer) > 500:
                    full_answer = full_answer[:500] + "..."
                return {'answer': f"Segundo as atas: {full_answer}", 'confidence': 0.75}
        
        # Busca por projetos ou temas específicos
        if any(term in q_lower for term in ['projeto', 'mapa', 'governo', 'economia', 'programa', 'iniciativa']):
            sentences = [s.strip() for s in context.split('.') if s.strip()]
            relevant_sentences = []
            
            # Limpa pontuação das palavras-chave
            keywords = [word.strip(string.punctuation) for word in q_lower.split() if len(word.strip(string.punctuation)) > 3]
            
            # Primeiro, identifica frases que contêm palavras-chave diretas
            for sentence in sentences:
                if sentence:
                    sentence_clean = sentence.lower()
                    if any(keyword in sentence_clean for keyword in keywords):
                        relevant_sentences.append(sentence)
            
            # Se encontrou pelo menos uma frase relevante, adiciona frases adjacentes para contexto
            if relevant_sentences:
                # Pega o índice da primeira frase relevante
                first_relevant_index = -1
                for i, sentence in enumerate(sentences):
                    if sentence in relevant_sentences:
                        first_relevant_index = i
                        break
                
                # Adiciona frases adjacentes (antes e depois) para contexto completo
                start_index = max(0, first_relevant_index - 1)
                end_index = min(len(sentences), first_relevant_index + 5)
                
                context_sentences = []
                for i in range(start_index, end_index):
                    if sentences[i] not in context_sentences:
                        context_sentences.append(sentences[i])
                
                relevant_sentences = context_sentences
            
            # Se não encontrou frases específicas, busca por contexto geral do tema
            if not relevant_sentences:
                tema_keywords = ['projeto', 'mapa', 'governo', 'economia', 'programa', 'iniciativa']
                for sentence in sentences:
                    if sentence and any(keyword in sentence.lower() for keyword in tema_keywords):
                        relevant_sentences.append(sentence)
            
            # Se ainda não encontrou, pega as primeiras frases que podem ser relevantes
            if not relevant_sentences and sentences:
                relevant_sentences = sentences[:5]
            
            if relevant_sentences:
                # Pega até 6 frases para uma resposta mais completa
                best_sentences = relevant_sentences[:6]
                combined_answer = '. '.join(best_sentences)
                if len(combined_answer) > 900:
                    combined_answer = combined_answer[:900] + "..."
                return {'answer': f"{combined_answer}", 'confidence': 0.75}
        
        # Busca genérica por palavras-chave
        keywords = [word for word in q_lower.split() if len(word) > 3 and word not in ['como', 'qual', 'onde', 'quando', 'quem', 'porque']]
        if keywords:
            sentences = [s.strip() for s in context.split('.') if s.strip()]
            scored_sentences = []
            
            for sentence in sentences[:8]:  # Analisa mais frases
                matches = sum(1 for keyword in keywords if keyword in sentence.lower())
                if matches > 0 and len(sentence) > 20:
                    scored_sentences.append((matches, sentence))
            
            # Ordena por relevância e pega as melhores
            scored_sentences.sort(key=lambda x: x[0], reverse=True)
            best_sentences = [sent[1] for sent in scored_sentences[:4]]
            
            if best_sentences:
                full_answer = '. '.join(best_sentences)
                if len(full_answer) > 700:
                    full_answer = full_answer[:700] + "..."
                return {'answer': f"{full_answer}", 'confidence': 0.7}
        
        # Resposta padrão mais natural
        return {'answer': "Não encontrei informações específicas sobre essa questão nas atas disponíveis.", 'confidence': 0.3}

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
        if hasattr(self, 'llm_type'):
            if self.llm_type == "ollama":
                model_name = getattr(self, 'model_name', 'desconhecido')
                model_status = f"Ollama - {model_name}"
            elif self.llm_type == "huggingface":
                model_status = "Hugging Face"
            else:
                model_status = "Sistema Interno"
        else:
            model_status = "Não detectado"
        
        return {
            'total_documents': len(self.documents),
            'last_update': self.last_update,
            'has_ai_model': hasattr(self, 'llm_type') and self.llm_type != "internal",
            'model_status': model_status,
            'model_type': getattr(self, 'llm_type', 'unknown')
        }
