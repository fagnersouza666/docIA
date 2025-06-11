# docIA - Sistema de Busca Inteligente de Documentos

Sistema avançado de busca e análise de documentos (atas, relatórios, etc.) usando IA generativa. Processa arquivos PDF, DOCX e TXT, oferecendo respostas inteligentes em linguagem natural com suporte a modelos locais (Ollama) para total privacidade.

## ✨ Funcionalidades

- **Busca Semântica**: Encontra informações por significado, não apenas por palavras-chave.
- **IA Generativa Local**: Usa Ollama para respostas naturais, mantendo os dados no seu ambiente.
- **Reindexação Automática**: Novos documentos na pasta `documents/` são indexados em tempo real.
- **Multi-Formato**: Suporta PDF, DOCX e TXT.
- **Fácil Deploy**: Containerizado com Docker para setup rápido.

## 🚀 Como Rodar

### Pré-requisitos
- Docker e Docker Compose
- (Opcional) Ollama para respostas de IA generativa de alta qualidade.

### Passos
1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/fagnersouza666/docIA.git
    cd docIA
    ```

2.  **Adicione seus documentos:**
    - Coloque seus arquivos (`.pdf`, `.docx`, `.txt`) na pasta `documents/`.

3.  **Inicie o sistema:**
    ```bash
    docker-compose up -d --build
    ```
    O sistema irá iniciar e indexar os documentos automaticamente.

4.  **Acesse a interface:**
    - Abra seu navegador em **http://localhost:5000**.

## ⚙️ Estrutura do Projeto

```
docIA/
├── documents/            # Pasta para seus documentos
├── smart_app.py          # Aplicação web (Flask)
├── smart_indexer.py      # Lógica de busca e IA
├── requirements.txt      # Dependências Python
├── Dockerfile.smart      # Definição do container
├── docker-compose.yml    # Orquestrador Docker
├── setup_ollama.py       # Script de ajuda para configurar Ollama
├── install.sh            # Script de instalação de dependências
└── README.md             # Este arquivo
```
