# Ambiente Inteligente (Sistemas Distribuídos 2023.2)

## Descrição do Projeto

Este repositório contém a implementação da segunda fase do projeto Ambiente Inteligente. Nesta etapa, desenvolvemos um ambiente inteligente que utiliza a tecnologia Protocol Buffers para definir mensagens e facilitar a comunicação entre o Gateway e os objetos (Dispositivos e Sensores) implementados em Python.

## Instruções de Uso

1. Primeiro, instale o Pipenv usando o pip:

   ```bash
   pip install pipenv
2. Em seguida, na pasta raiz do projeto, configure suas variáveis de ambiente no arquivo .env. Para criar o arquivo .env, basta copiar o arquivo .env.example:
    ```bash
    cp .env.example .env
3. Depois, instale as dependências:
    ```bash
    pipenv install && pipenv install -d

## Execução
1. Em um terminal, execute o seguinte comando para iniciar o Gateway:
    ```bash
    python gateway.py
2. Repita o processo para iniciar os dispositivos:
    ```bash
    python thermostat.py
    ```
    ```bash
    python airconditioner.py
