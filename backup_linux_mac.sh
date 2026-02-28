#!/bin/bash
################################################################################
# Automated Backup Script for LAN Dashboard
# Creates daily backup with timestamp
# Schedule with cron: 0 18 * * * /path/to/backup.sh
################################################################################

echo ""
echo "==============================================="
echo "  LAN Dashboard - Automated Backup"
echo "==============================================="
echo ""

# Configuration - EDIT THESE PATHS
SOURCE="$HOME/LAN_Dashboard/data/project_data.xlsx"
BACKUP_DIR="$HOME/LAN_Dashboard/data/backups"
LOG_FILE="$HOME/LAN_Dashboard/logs/backup.log"

# Create backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/project_data_$TIMESTAMP.xlsx"

# Create directories if they don't exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$HOME/LAN_Dashboard/logs"

# Check if source file exists
if [ ! -f "$SOURCE" ]; then
    echo "[ERROR] Source file not found: $SOURCE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - [ERROR] Source file not found" >> "$LOG_FILE"
    exit 1
fi

# Create backup
echo "Creating backup..."
echo "Source: $SOURCE"
echo "Destination: $BACKUP_FILE"
echo ""

cp "$SOURCE" "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "[SUCCESS] Backup created successfully!"
    echo "File: $BACKUP_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - [SUCCESS] Backup created: $BACKUP_FILE" >> "$LOG_FILE"
    
    # Get file size
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "Size: $SIZE"
else
    echo "[ERROR] Backup failed!"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - [ERROR] Backup failed" >> "$LOG_FILE"
    exit 1
fi

# Delete backups older than 30 days
echo ""
echo "Cleaning old backups (older than 30 days)..."
find "$BACKUP_DIR" -name "*.xlsx" -type f -mtime +30 -delete
echo "Cleanup complete."

# Display backup statistics
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.xlsx 2>/dev/null | wc -l)
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)

echo ""
echo "Statistics:"
echo "  Total backups: $BACKUP_COUNT"
echo "  Total size: $BACKUP_SIZE"

echo ""
echo "==============================================="
echo "  Backup Complete!"
echo "==============================================="
echo ""

exit 0
