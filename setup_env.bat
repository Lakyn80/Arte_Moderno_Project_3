@echo off
echo === Aktivace virtualenv s Pythonem 3.11 ===

REM ✅ Nastav cestu k Pythonu 3.11 - pokud nemáš, stáhni z python.org
SET PYTHON_EXE=C:\Users\lukas\AppData\Local\Programs\Python\Python311\python.exe

IF NOT EXIST %PYTHON_EXE% (
    echo Python 3.11 nebyl nalezen na %PYTHON_EXE%
    echo Nainstaluj ho prosím z https://www.python.org/downloads/release/python-3110/
    pause
    exit /b
)

REM ✅ Smazání původního venv, pokud existuje
IF EXIST venv (
    echo - Mazání starého virtuálního prostředí...
    rmdir /s /q venv
)

REM ✅ Vytvoření nového virtuálního prostředí
echo - Vytvářím nové prostředí s Pythonem 3.11...
%PYTHON_EXE% -m venv venv

REM ✅ Aktivace venv
call venv\Scripts\activate.bat

REM ✅ Upgrade pip
echo - Aktualizuji pip...
python -m pip install --upgrade pip

REM ✅ Instalace requirements
echo - Instaluji balíčky z requirements.txt...
pip install -r requirements.txt

echo === HOTOVO! Spusť aplikaci: python run.py ===
pause
