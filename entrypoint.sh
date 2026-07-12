#!/bin/bash
ollama serve &

until ollama list > /dev/null 2>&1; do
    echo "Waiting for ollama..."
    sleep 1
done

#ollama pull llama3.1:8b

python3 -u main.py