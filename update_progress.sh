#!/bin/bash

# SideQuest Progress Updater
# Usage: ./update_progress.sh [action] [description]
# Actions: complete, start, note

PROGRESS_FILE="PROGRESS.md"
DATE=$(date "+%B %d, %Y")

case "$1" in
    "complete")
        echo "✅ Marking task as complete: $2"
        # Update the last updated date
        sed -i "s/\*\*Last Updated:\*\* .*/\*\*Last Updated:\*\* $DATE/" $PROGRESS_FILE
        # Could add logic to move items from "In Progress" to "Completed"
        ;;
    "start")
        echo "🚧 Starting new task: $2"
        sed -i "s/\*\*Last Updated:\*\* .*/\*\*Last Updated:\*\* $DATE/" $PROGRESS_FILE
        ;;
    "note")
        echo "📝 Adding note: $2"
        sed -i "s/\*\*Last Updated:\*\* .*/\*\*Last Updated:\*\* $DATE/" $PROGRESS_FILE
        echo "- $DATE: $2" >> temp_note.txt
        # Insert the note into the Notes section
        ;;
    "phase")
        echo "🎯 Phase transition: $2"
        sed -i "s/\*\*Last Updated:\*\* .*/\*\*Last Updated:\*\* $DATE/" $PROGRESS_FILE
        sed -i "s/\*\*Current Phase:\*\* .*/\*\*Current Phase:\*\* $2/" $PROGRESS_FILE
        ;;
    *)
        echo "Usage: ./update_progress.sh [complete|start|note|phase] [description]"
        echo ""
        echo "Examples:"
        echo "  ./update_progress.sh complete 'MinIO integration working'"
        echo "  ./update_progress.sh start 'Building media upload component'"
        echo "  ./update_progress.sh note 'Found issue with file size limits'"
        echo "  ./update_progress.sh phase 'Phase 2 Complete → Moving to Phase 3'"
        exit 1
        ;;
esac

echo "Progress file updated! Last modified: $DATE"