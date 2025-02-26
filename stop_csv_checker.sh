#!/bin/bash

# Script to stop the CSV checker process

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if PID file exists
if [ -f .csv_checker.pid ]; then
    PID=$(cat .csv_checker.pid)
    
    # Check if process is still running
    if ps -p $PID > /dev/null; then
        echo "Stopping CSV checker process (PID: $PID)..."
        kill $PID
        
        # Wait for process to terminate
        sleep 2
        if ps -p $PID > /dev/null; then
            echo "Process didn't terminate gracefully, forcing..."
            kill -9 $PID
        fi
        
        echo "CSV checker stopped."
    else
        echo "CSV checker process is not running (PID: $PID)."
    fi
    
    # Remove PID file
    rm .csv_checker.pid
else
    # Try to find and kill any running instances
    PIDS=$(pgrep -f "python check_and_fix_csv.py")
    if [ -n "$PIDS" ]; then
        echo "Found CSV checker processes: $PIDS"
        echo "Stopping all CSV checker processes..."
        pkill -f "python check_and_fix_csv.py"
        echo "CSV checker processes stopped."
    else
        echo "No CSV checker processes found."
    fi
fi 