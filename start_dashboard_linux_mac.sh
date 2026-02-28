#!/bin/bash
################################################################################
# LAN Dashboard Startup Script (Linux/Mac)
# Starts the Streamlit dashboard automatically
################################################################################

echo ""
echo "==============================================="
echo "  Starting LAN Dashboard..."
echo "==============================================="
echo ""

# Configuration - EDIT THESE PATHS
DASHBOARD_DIR="$HOME/LAN_Dashboard"
PYTHON_PATH="python3"
APP_FILE="app_enhanced.py"
LOG_FILE="$DASHBOARD_DIR/logs/startup.log"

# Create logs directory if it doesn't exist
mkdir -p "$DASHBOARD_DIR/logs"

# Log startup
echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting dashboard" >> "$LOG_FILE"

# Change to dashboard directory
cd "$DASHBOARD_DIR" || {
    echo "[ERROR] Dashboard directory not found: $DASHBOARD_DIR"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - [ERROR] Directory not found" >> "$LOG_FILE"
    exit 1
}

# Check if app file exists
if [ ! -f "$APP_FILE" ]; then
    echo "[ERROR] Application file not found: $APP_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - [ERROR] App file not found" >> "$LOG_FILE"
    exit 1
fi

echo "Dashboard directory: $DASHBOARD_DIR"
echo "Application file: $APP_FILE"
echo ""
echo "Starting dashboard..."
echo ""
echo "Once started, the dashboard will open in your browser at:"
echo "http://localhost:8501"
echo ""
echo "Keep this terminal open - DO NOT CLOSE!"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Start the dashboard
$PYTHON_PATH -m streamlit run "$APP_FILE" --server.headless true

# Log shutdown
echo "$(date '+%Y-%m-%d %H:%M:%S') - Dashboard stopped" >> "$LOG_FILE"

echo ""
echo "Dashboard has stopped."
