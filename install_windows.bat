@echo off
echo Iniciando instalacao das dependencias para Windows...

REM Verifica se o Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado. Por favor, instale o Python de https://www.python.org/downloads/
    echo Certifique-se de marcar a opcao "Add Python to PATH" durante a instalacao
    pause
    exit /b 1
)

REM Verifica se o pip esta instalado
pip --version >nul 2>&1
if errorlevel 1 (
    echo Pip nao encontrado. Instalando pip...
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    del get-pip.py
)

REM Instala as dependências do requirements.txt
echo Instalando dependencias do requirements.txt...
pip install -r requirements.txt

echo Instalacao concluida!
pause 