import requests
import subprocess
import time
import os

def check_ollama():
    """Verifica se o Ollama está instalado e rodando."""
    print("Verificando instalação do Ollama...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama detectado com {len(models)} modelo(s).")
            return True
    except requests.exceptions.RequestException:
        print("Ollama não parece estar rodando.")
    return False

def install_ollama_instructions():
    """Mostra instruções de instalação para o Ollama."""
    print("\n--- Como Instalar o Ollama ---")
    print("1. Baixe em: https://ollama.ai/download")
    print("2. Execute o instalador.")
    print("3. (Opcional) Para usar um modelo, abra o terminal e rode: ollama pull llama2")
    input("\nPressione ENTER após instalar e rodar o Ollama para continuar...")

def main():
    if not check_ollama():
        install_ollama_instructions()
        if not check_ollama():
            print("Não foi possível conectar ao Ollama. O sistema usará um modelo de fallback (HuggingFace).")
            return

    print("\nConfiguração do Ollama concluída com sucesso!")

if __name__ == "__main__":
    main()
