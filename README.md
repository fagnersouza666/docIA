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

### Opção 2: Execução com Kubernetes (Produção)

1. **Deploy no Kubernetes:**

   ```bash
   # Windows
   deploy-k8s.bat
   
   # Linux/Mac
   ./deploy-k8s.sh
   ```

   O script automaticamente:
   - Constrói a imagem Docker
   - Cria namespace e recursos do K8s
   - Configura volumes persistentes
   - Expõe a aplicação na porta 30500

2. **Acesse**: <http://localhost:30500>

### Opção 3: Execução com Docker Compose

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

## ☸️ Kubernetes - Enterprise Edition

### Deploy Rápido com Makefile

```bash
# Ver todos os comandos disponíveis
make help

# Build e deploy completo
make build && make deploy

# Deploy rápido (sem build)
make quick-deploy

# Verificar status
make status

# Ver logs
make logs
```

### Deploy Manual

#### Windows

```bash
# Setup do cluster (se necessário)
setup-remote-k8s.bat

# Deploy completo com interface interativa
deploy\deploy.bat
```

#### Linux/Mac

```bash
# Setup do cluster (se necessário)
chmod +x setup-remote.sh && ./setup-remote.sh

# Deploy completo com interface interativa
chmod +x deploy/deploy.sh && ./deploy/deploy.sh
```

### Recursos Enterprise

#### Segurança

- **RBAC**: Service accounts com permissions mínimas
- **Security Context**: Execução não-root
- **Network Policies**: Isolamento de rede
- **Secrets**: Gerenciamento seguro de credenciais

#### Observabilidade

- **Health Checks**: Liveness, Readiness e Startup probes
- **Metrics**: Prometheus integration
- **Logging**: Structured logs com forwarding
- **Monitoring**: Grafana dashboards

#### Escalabilidade

- **HPA**: Auto-scaling baseado em CPU/memória
- **Resource Management**: Limits e requests configurados
- **Rolling Updates**: Zero-downtime deployments
- **Multiple Environments**: Dev, Staging, Produção

### Configurações por Ambiente

| Ambiente | Replicas | CPU Request | Memory Request | Storage Class |
|----------|----------|-------------|----------------|---------------|
| Development | 1 | 500m | 1Gi | standard |
| Staging | 2 | 1000m | 2Gi | fast-ssd |
| Production | 3 | 2000m | 4Gi | fast-ssd |

### Recursos Provisionados

- **Namespace**: doc-ia com labels padronizadas
- **Deployment**: Multi-replica com rolling updates
- **Services**: ClusterIP, NodePort e Headless
- **PVCs**: Documentos (20Gi), Cache (10Gi), Logs (5Gi)
- **Ingress**: nginx com SSL/TLS e rate limiting
- **ConfigMap**: Configuração estruturada
- **Secrets**: Credenciais criptografadas
- **RBAC**: Service accounts com permissions mínimas
- **HPA**: Auto-scaling configurado
- **Network Policies**: Segurança de rede
- **Monitoring**: ServiceMonitor e dashboards

### Comandos de Gerenciamento

```bash
# Escalabilidade
make scale REPLICAS=5

# Atualização
make update

# Backup
make backup

# Restauração
make restore BACKUP_FILE=backup/file.yaml

# Debug
make debug

# Limpeza
make clean

# Deletar tudo
make delete
```

### Monitoramento

```bash
# Health check completo
make health

# Monitorar recursos
make monitor

# Ver eventos
make events

# Testar conectividade
make test
```

### Troubleshooting

```bash
# Logs detalhados
make logs-tail

# Conectar ao pod
make dev-shell

# Descrever deployment
make describe

# Testar rede
make network-test
```

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
├── docker-compose.yml     # Orquestração Docker
├── k8s-*.yaml            # Manifests do Kubernetes
├── deploy-k8s.sh         # Script de deploy K8s (Linux/Mac)
├── deploy-k8s.bat        # Script de deploy K8s (Windows)
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

**v2.3.0** - Enterprise Kubernetes Edition

- **🔒 Segurança Enterprise**: RBAC, Security Context, Network Policies, Secrets Management
- **📊 Observabilidade**: Health checks avançados, Prometheus metrics, Grafana dashboards
- **⚡ Escalabilidade**: HPA com auto-scaling, Resource management otimizado
- **🔄 Rolling Updates**: Zero-downtime deployments com múltiplos ambientes
- **💾 Storage Avançado**: Volumes persistentes com backup strategy configurado
- **🛠️ DevOps Ready**: Makefile com 25+ comandos, Scripts de deploy interativos
- **🌐 Multi-Ambiente**: Configurações específicas para Dev, Staging e Produção
- **🔍 Monitoring**: ServiceMonitor, Log forwarding, Network policies de segurança

### Funcionalidades Enterprise Adicionadas

- ✅ RBAC com service accounts seguros
- ✅ Security contexts não-root
- ✅ Network policies para isolamento
- ✅ Secrets para dados sensíveis
- ✅ HPA com auto-scaling inteligente
- ✅ Health checks robustos (liveness, readiness, startup)
- ✅ Prometheus + Grafana integration
- ✅ Volumes com backup automatizado
- ✅ Scripts de deploy interativos (Windows/Linux)
- ✅ Makefile com comandos de gerenciamento
- ✅ Configurações por ambiente (dev/staging/prod)
- ✅ TLS/SSL com cert-manager
- ✅ Rate limiting no Ingress

---

**💡 Dica**: Para melhor experiência, use sempre o Ollama + Mistral. O sistema funciona sem ele, mas a qualidade das respostas é significativamente superior com IA local!
