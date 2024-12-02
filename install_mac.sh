#!/bin/bash

echo "Iniciando instalação das dependências para macOS..."

# Verifica se o Homebrew está instalado
if ! command -v brew &> /dev/null; then
    echo "Homebrew não encontrado. Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python não encontrado. Instalando Python..."
    brew install python3
fi

# Verifica se o pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "Pip não encontrado. Instalando pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi

# Instala as dependências do requirements.txt
echo "Instalando dependências do requirements.txt..."
pip3 install -r requirements.txt

echo "Instalação concluída!" 