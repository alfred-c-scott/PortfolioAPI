#!/bin/bash
pid=$(ps aux | grep '[u]vicorn app.main:app --port 8030' | awk '{print $2}')
if [ -n "$pid" ]; then
    kill -9 $pid
    echo "Uvicorn process $pid terminated"
else
    echo "No matching Uvicorn process found"
fi