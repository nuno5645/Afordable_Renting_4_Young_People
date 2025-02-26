#!/bin/bash

# Script to run the CSV checker in the background

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if a CSV checker process is already running
if pgrep -f "python check_and_fix_csv.py" > /dev/null; then
    echo "CSV checker is already running."
    exit 0
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Get current timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Run the CSV checker in the background with specified interval (default: 30 minutes)
INTERVAL=${1:-30}
nohup python check_and_fix_csv.py --interval $INTERVAL > logs/csv_checker_$TIMESTAMP.log 2>&1 &

# Save the process ID
echo $! > .csv_checker.pid
echo "CSV checker started with PID $! (checking every $INTERVAL minutes)"
echo "Logs are being written to logs/csv_checker_$TIMESTAMP.log" 