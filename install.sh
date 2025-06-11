#!/bin/bash
echo "--- Iniciando Instalação do Sistema docIA ---"

# 1. Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null
then
    echo "Python 3 não encontrado. Por favor, instale-o para continuar."
    exit 1
fi
echo "✅ Python 3 verificado."

# 2. Verificar se pip está instalado
if ! command -v pip3 &> /dev/null
then
    echo "pip3 não encontrado. Por favor, instale-o."
    exit 1
fi
echo "✅ pip verificado."

# 3. Criar ambiente virtual
if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv .venv
fi
echo "✅ Ambiente virtual pronto."

# 4. Ativar ambiente virtual e instalar dependências
echo "Instalando dependências do requirements.txt..."
source .venv/bin/activate
pip3 install -r requirements.txt
deactivate
echo "✅ Dependências instaladas."

# 5. Verificar Docker e Docker Compose
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null
then
    echo "⚠️ Docker ou Docker Compose não encontrados."
    echo "Para rodar o sistema com Docker, por favor, instale-os."
    echo "Instruções: https://docs.docker.com/get-docker/"
else
    echo "✅ Docker e Docker Compose verificados."
fi

echo "\n--- Instalação Concluída! ---"
echo "Para rodar o sistema:"
echo "1. Coloque seus documentos na pasta 'documents/'."
echo "2. Rode 'docker-compose up -d --build'."
echo "3. Acesse http://localhost:5000 no seu navegador."
