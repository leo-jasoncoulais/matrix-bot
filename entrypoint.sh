#!/bin/bash
ollama serve &
OLLAMA_PID=$!

until ollama list > /dev/null 2>&1; do
    echo "Waiting for ollama..."
    sleep 1
done

trap 'kill -TERM $OLLAMA_PID $PYTHON_PID 2>/dev/null; wait' TERM INT

python3 -u main.py &
PYTHON_PID=$!
wait $PYTHON_PID