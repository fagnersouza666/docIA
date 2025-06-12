# Changelog - docIA

Todas as mudanças importantes do projeto serão documentadas aqui.

## [2.2.0] - 2024-12-19 18:30

### ✨ Melhorias no Mistral

- **Prompt otimizado**: Prompt mais direto e eficaz para respostas detalhadas
- **Parâmetros ajustados**: Temperature 0.8, tokens 500, top_k 40 para melhor qualidade
- **Dockerfile corrigido**: Script de inicialização que garante Ollama + Mistral funcionando
- **Logs limpos**: Removidos emojis para compatibilidade com terminal Windows
- **Força Mistral**: Modelo obrigatório, sem detecção automática

### 🔧 Correções Técnicas

- Corrigido problema de inicialização do Ollama no container
- Melhorado script start.sh com sequência de carregamento adequada
- Removidos problemas de encoding nos logs

## [2.1.0] - 2025-06-12

### 🎯 MODELO MISTRAL COMO PADRÃO OBRIGATÓRIO

#### ✅ Adicionado

- **Priorização automática do modelo Mistral** - Sistema sempre tenta usar Mistral como primeira opção
- **Detecção inteligente de modelos Mistral** - Procura especificamente por variantes do Mistral nos modelos disponíveis
- **Configuração padrão atualizada** - `OLLAMA_MODEL=mistral` configurado em todo o sistema
- **Docker otimizado** - Dockerfile automaticamente instala Ollama + Mistral
- **Fallback inteligente** - Sistema interno apenas quando IA não está disponível

#### 🔧 Modificado

- **smart_indexer.py**: Lógica de inicialização prioriza Mistral sobre outros modelos
- **README.md**: Documentação completamente reescrita focando no Mistral
- **Configurações Docker**: Mistral pré-configurado no container
- **Interface**: Status mostra claramente qual modelo está sendo usado

#### 🧠 Inteligência de Modelo

- Sistema detecta automaticamente se Mistral está disponível
- Procura por variantes do Mistral ("mistral", "mistral:latest", etc.)
- Fallback para outros modelos apenas se Mistral não estiver disponível
- Variável de ambiente `OLLAMA_MODEL` força uso do Mistral

#### 📋 Para Usuários

- **Experiência Otimizada**: Qualidade máxima de respostas com Mistral
- **Setup Simplificado**: Docker configura tudo automaticamente
- **Compatibilidade**: Sistema funciona mesmo sem Ollama (modo degradado)

## [2.1.1] - 2025-06-11

### 🎨 INTERFACE MELHORADA E RESPOSTAS EXPANDIDAS

#### ✅ Adicionado

- **Área de resposta expandida** - Interface com área significativamente maior para respostas
- **Design moderno** - Gradientes, sombras e efeitos visuais melhorados
- **Tipografia aprimorada** - Fonte maior e espaçamento otimizado para leitura
- **Animações suaves** - Transições e efeitos hover para melhor UX

#### 🔧 Modificado

- **Container expandido** - Layout mais amplo para melhor visualização
- **Respostas mais longas** - Limite aumentado para até 900 caracteres
- **Análise contextual** - Chunks maiores e análise de frases adjacentes
- **CSS otimizado** - Estilização moderna e responsiva

## [2.1.0] - 2025-06-10

### 🧠 SISTEMA DE RESPOSTAS NATURAIS INTERNO

#### ✅ Adicionado

- **Sistema interno de IA** - Funciona sem modelos externos obrigatórios
- **Respostas em linguagem natural** - Elimina citações de trechos, foca em respostas diretas
- **Detecção inteligente de entidades** - Reconhece datas, nomes, valores monetários automaticamente
- **Análise contextual avançada** - Compreende contexto para gerar respostas relevantes
- **Status detalhado** - Interface mostra qual modelo de IA está sendo usado

#### 🔧 Modificado

- **Arquitetura híbrida** - Prioriza Ollama quando disponível, funciona independentemente
- **Interface atualizada** - Mostra status do modelo e qualidade esperada
- **Lógica de fallback** - Sistema interno robusto quando IA externa não está disponível

#### 🚫 Removido

- **Dependência obrigatória** - Ollama agora é opcional (mas recomendado)
- **Citações de arquivos** - Sistema foca em respostas naturais

## [2.0.1] - 2025-06-08

### 🔧 Correções e Melhorias

#### ✅ Corrigido

- **Erro de indexação** - Problema com documentos vazios
- **Performance de busca** - Otimização do algoritmo TF-IDF
- **Detecção de arquivos** - Melhoria no monitoramento automático

#### 🔧 Modificado

- **Logs mais informativos** - Mensagens de debug detalhadas
- **Tratamento de erros** - Melhor handling de exceções
- **Validação de entrada** - Verificação de queries vazias

## [2.0.0] - 2025-06-05

### 🚀 VERSÃO MAJOR - SUPORTE A IA EXTERNA

#### ✅ Adicionado

- **Integração com Ollama** - Suporte para modelos locais de IA
- **Busca semântica avançada** - Algoritmos TF-IDF + similaridade cosseno
- **Interface web moderna** - UI/UX completamente redesenhada
- **Monitoramento automático** - Detecção de novos arquivos em tempo real
- **Sistema de chunks** - Divisão inteligente de documentos grandes
- **Docker completo** - Containerização com suporte a IA

#### 🔧 Modificado

- **Arquitetura modular** - Separação clara entre indexação e busca
- **Performance otimizada** - Indexação e busca mais rápidas
- **Suporte multi-formato** - PDF, DOCX, TXT com parsers otimizados

## [1.0.0] - 2025-05-30

### 🎉 VERSÃO INICIAL

#### ✅ Funcionalidades Básicas

- **Indexação de documentos** - PDF, DOCX, TXT
- **Busca por palavras-chave** - Sistema básico de busca
- **Interface simples** - Web interface minimalista
- **API REST** - Endpoints básicos para busca

---

## [2.0.0] - Versão Anterior

- Sistema de busca semântica com TF-IDF
- Suporte a PDF, DOCX e TXT
- Interface web com Flask
- Reindexação automática de documentos
- Integração básica com Ollama
