@echo off
title Galvanos Calc
color 02
cls

echo =======================================================
echo          SISTEMA DE GESTAO: GCalc
echo =======================================================
echo [SISTEMA] Iniciando processo local...

:: Navega ate o diretorio do projeto
cd /d "C:\Users\Merotec\Desktop\app-master"

:: 2. Ativa o ambiente virtual
if not exist .venv (
    color 0C
    echo [ERRO] Ambiente .venv nao encontrado em: %cd%
    echo [AVISO] criando ambiente .venv...
    python -m venv .runenv
    echo [AVISO] Ambiente .runenv criado em: %cd%	
    pause
    exit
)

echo [VENV] Ativando ambiente virtual...
call .runenv\Scripts\activate
:: call .runenv\Scripts\python main.py
:: Mantém o terminal aberto e pronto para novos comandos
cmd /k