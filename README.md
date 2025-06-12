# docIA - Sistema de Busca Inteligente de Documentos

O **docIA** é uma aplicação para busca e análise de documentos que utiliza IA generativa local para preservar a privacidade. O projeto processa arquivos nos formatos **PDF**, **DOCX** e **TXT**, permitindo consultas em linguagem natural e oferecendo resultados relevantes por meio de busca semântica.

## ✨ Recursos Principais

- **Busca Semântica** – Encontre informações pelo significado do texto, não apenas por palavras-chave.
- **IA Generativa Local** – Usa o Ollama para gerar respostas de forma privada, sem enviar seus dados para a nuvem.
- **Reindexação Automática** – Novos arquivos adicionados à pasta `documents/` são processados e indexados em tempo real.
- **Suporte Multi‑Formato** – Aceita documentos em PDF, DOCX e TXT.
- **Deploy Simplificado** – Projeto containerizado com Docker para execução rápida em qualquer ambiente.

## 🚀 Como Executar

### Pré‑requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/)
- [Ollama](https://github.com/ollama/ollama) – já incluído no container para gerar as respostas de IA

### Passo a Passo

1. **Clone o repositório**

   ```bash
   git clone https://github.com/fagnersouza666/docIA.git
   cd docIA
   ```

2. **Adicione seus documentos**

   Coloque arquivos `.pdf`, `.docx` ou `.txt` na pasta `documents/` (crie-a se ainda não existir).

3. **Inicie o sistema**

   ```bash
   docker-compose up -d --build
   ```

   O serviço irá iniciar o Ollama automaticamente, baixar o modelo padrão se necessário e indexar os documentos encontrados.

4. **Acesse a interface**

   Abra o navegador em [http://localhost:5000](http://localhost:5000) para realizar buscas.

## ⚙️ Estrutura do Projeto

```
docIA/
├── documents/            # Pasta para seus documentos
├── smart_app.py          # Aplicação web (Flask)
├── smart_indexer.py      # Lógica de busca e IA
├── requirements.txt      # Dependências Python
├── Dockerfile.smart      # Definição do container
├── docker-compose.yml    # Orquestrador Docker
└── README.md             # Este arquivo
```

