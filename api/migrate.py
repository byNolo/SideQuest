#!/usr/bin/env python3
"""
Migration helper script for SideQuest
"""
import os
import subprocess
import sys
from config import Config

def run_command(cmd, cwd=None):
    """Run a command and return its output"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [init|revision|upgrade|downgrade]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # For local development, we might need to use a local DB URL
    if "db:5432" in Config.DATABASE_URL:
        print("Warning: Using Docker DB URL. Make sure database is accessible.")
        print("Consider setting DATABASE_URL=postgresql+psycopg2://sidequest:sidequest@localhost:5432/sidequest for local dev")
    
    if command == "init":
        run_command("alembic init alembic")
    elif command == "revision":
        message = input("Migration message: ") or "auto migration"
        run_command(f"alembic revision --autogenerate -m '{message}'")
    elif command == "upgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else "head"
        run_command(f"alembic upgrade {target}")
    elif command == "downgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else "-1"
        run_command(f"alembic downgrade {target}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
