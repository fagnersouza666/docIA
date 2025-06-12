# DocIA - Sistema de Busca Inteligente de Documentos 🧠📚

Sistema avançado de busca e análise de documentos com IA, oferecendo respostas em linguagem natural baseadas no conteúdo dos seus arquivos.

## 🚀 Características Principais

- **Busca Semântica Inteligente**: Encontra informações mesmo sem correspondência exata de palavras
- **Respostas em Linguagem Natural**: IA gera respostas diretas e contextualizadas
- **Múltiplos Formatos**: Suporte para PDF, DOCX e TXT
- **Interface Web Moderna**: Interface limpa e responsiva
- **Monitoramento Automático**: Detecta alterações nos documentos automaticamente
- **IA Local**: Usa Ollama com modelo Mistral para máxima privacidade

## 📋 Pré-requisitos

- **Python 3.8+**
- **Para execução local**: Ollama + modelo Mistral (recomendado)
- **Para execução com Docker**: Docker e Docker Compose

## 🔧 Instalações

### Opção 1: Execução Local (Recomendada)

1. **Instale o Ollama:**
   - Baixe de: <https://ollama.com/download>
   - Execute o instalador
   - Reinicie o terminal

2. **Baixe o modelo Mistral:**

   ```bash
   ollama pull mistral
   ```

3. **Clone e configure o projeto:**

   ```bash
   git clone [seu-repositorio]
   cd docIA
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   
   pip install -r requirements.txt
   ```

4. **Execute:**

   ```bash
   python smart_app.py
   ```

### Opção 2: Execução com Docker

1. **Execute com Docker Compose:**

   ```bash
   docker-compose up --build
   ```

   O Docker automaticamente:
   - Instala o Ollama
   - Baixa o modelo Mistral
   - Configura tudo para funcionar

## 📝 Como Usar

1. **Adicione seus documentos** na pasta `documents/`
2. **Acesse**: <http://localhost:5000>
3. **Faça perguntas** sobre o conteúdo dos documentos
4. **Reindexe** quando adicionar novos arquivos (ou aguarde a detecção automática)

### Exemplos de Perguntas

- "Quais foram as principais decisões da última reunião?"
- "Há alguma menção sobre orçamento?"
- "Quem foram os participantes da reunião de março?"
- "Resumo dos pontos discutidos sobre marketing"

## 🧠 Modelos de IA

O sistema prioriza sempre o **modelo Mistral via Ollama** para máxima qualidade e privacidade:

1. **🎯 Mistral (Padrão)**: Modelo local de alta qualidade
2. **⚠️ Sistema Interno**: Fallback se Ollama não estiver disponível

### Configuração do Modelo

O sistema está configurado para usar sempre o **Mistral** como padrão:

- **Localmente**: Detecta automaticamente se Mistral está disponível
- **Docker**: Automaticamente baixa e configura o Mistral
- **Variável de ambiente**: `OLLAMA_MODEL=mistral` (já configurado)

## 📊 Status do Sistema

A interface mostra:

- ✅ **Ollama - mistral**: Funcionando perfeitamente
- ⚠️ **Sistema Interno**: Funcional, mas qualidade limitada

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

```bash
OLLAMA_MODEL=mistral          # Força uso do Mistral
FLASK_ENV=production          # Modo de produção
TRANSFORMERS_CACHE=/app/.cache # Cache dos modelos
```

### Personalização

- **Tamanho dos chunks**: Modifique `chunk_size` em `smart_indexer.py`
- **Número de resultados**: Ajuste `max_results` nas buscas
- **Threshold de similaridade**: Configure em `_semantic_search`

## 🐳 Detalhes do Docker

O `Dockerfile.smart` inclui:

- Instalação automática do Ollama
- Download do modelo Mistral
- Configuração de cache otimizada
- Inicialização automática dos serviços

## 📁 Estrutura do Projeto

```
docIA/
├── smart_app.py           # Aplicação Flask principal
├── smart_indexer.py       # Motor de busca e IA
├── documents/             # Pasta dos documentos
├── Dockerfile.smart       # Container com Ollama+Mistral
├── docker-compose.yml     # Orquestração completa
├── requirements.txt       # Dependências Python
└── README.md             # Este arquivo
```

## 🚀 Performance

- **Indexação**: ~100 documentos/minuto
- **Busca**: <1 segundo por consulta
- **Memória**: ~200MB base + modelo IA
- **CPU**: Otimizado para uso eficiente

## 🔒 Privacidade

- **100% Local**: Nenhum dado sai da sua máquina
- **Sem APIs externas**: Modelo IA roda localmente
- **Controle total**: Você possui todos os dados

## 🛠️ Troubleshooting

### Problema: "Sistema Interno" em vez de Mistral

**Solução:**

1. Verifique se Ollama está rodando: `ollama list`
2. Instale o Mistral: `ollama pull mistral`
3. Reinicie a aplicação

### Problema: Baixa qualidade nas respostas

**Solução:**

1. Instale o Ollama + Mistral (modelo mais poderoso)
2. Adicione mais documentos relevantes
3. Reformule a pergunta de forma mais específica

### Problema: Documentos não indexados

**Solução:**

1. Verifique se estão na pasta `documents/`
2. Clique em "Reindexar" na interface
3. Verifique os logs no terminal

## 📊 Versão Atual

**v2.2.0** - Mistral Otimizado

- Prompt melhorado para respostas mais detalhadas
- Configurações de temperatura e tokens otimizadas
- Dockerfile corrigido para garantir inicialização do Ollama
- Logs simplificados sem emojis para compatibilidade
- Força uso do Mistral como modelo obrigatório

- ✅ Modelo Mistral configurado como padrão
- ✅ Priorização automática do Ollama+Mistral
- ✅ Fallback inteligente se IA não estiver disponível
- ✅ Interface atualizada com status do modelo
- ✅ Docker otimizado com Mistral pré-configurado

---

**💡 Dica**: Para melhor experiência, use sempre o Ollama + Mistral. O sistema funciona sem ele, mas a qualidade das respostas é significativamente superior com IA local!
