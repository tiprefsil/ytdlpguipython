#!/bin/bash

echo "Iniciando instalação das dependências..."

# Verifica se o pip está instalado
if ! command -v pip &> /dev/null; then
    echo "Pip não encontrado. Instalando pip..."
    sudo apt-get update
    sudo apt-get install python3-pip -y
fi

# Instala as dependências do requirements.txt
echo "Instalando dependências do requirements.txt..."
pip install -r requirements.txt

echo "Instalação concluída!" 