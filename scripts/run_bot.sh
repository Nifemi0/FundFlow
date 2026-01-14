#!/bin/bash

# Institutional Bot Supervisor
# Ensures the FundFlow bot stays active and restarts on failure.

# Configuration
PROJECT_DIR="/root/.gemini/antigravity/scratch/fundflow"
VENV_PATH="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/supervisor.log"

mkdir -p "$LOG_DIR"

echo "[$(date)] Supervisor started. Monitoring FundFlow Bot..." | tee -a "$LOG_FILE"

while true; do
    echo "[$(date)] Starting FundFlow Bot..." | tee -a "$LOG_FILE"
    
    # Run the bot and capture exit code
    # We use PYTHONPATH to ensure modules are found correctly
    cd "$PROJECT_DIR"
    PYTHONPATH=. "$VENV_PATH/bin/python3" bot/main.py >> "$LOG_DIR/bot.log" 2>&1
    
    EXIT_CODE=$?
    
    echo "[$(date)] Bot exited with code $EXIT_CODE." | tee -a "$LOG_FILE"
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[$(date)] Graceful shutdown detected. Exiting supervisor." | tee -a "$LOG_FILE"
        exit 0
    fi
    
    echo "[$(date)] Crash detected. Restarting in 5 seconds..." | tee -a "$LOG_FILE"
    sleep 5
done
