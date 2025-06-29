#!/usr/bin/env python3
"""
Setup script for the On-Premises Multi-Agent Task Manager System.

This script helps users set up the project environment and dependencies.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_uv_installation():
    """Check if uv is installed."""
    print("📦 Checking uv installation...")
    if shutil.which("uv") is None:
        print("❌ uv is not installed")
        print("Please install uv first:")
        print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False
    print("✅ uv is installed")
    return True


def setup_project():
    """Set up the project environment."""
    print("🚀 Setting up On-Premises Multi-Agent Task Manager System")
    print("=" * 60)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_uv_installation():
        return False
    
    # Create data directory
    print("📁 Creating data directory...")
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory created")
    
    # Install dependencies
    if not run_command("uv sync", "Installing dependencies"):
        return False
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = """# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8002

# A2A Configuration
A2A_SERVER_HOST=localhost
A2A_SERVER_PORT=8001

# Database Configuration
DATABASE_PATH=./data/tasks.db

# Logging Configuration
LOG_LEVEL=INFO
DEBUG=false

# Agent Configuration
TASK_MANAGER_AGENT_NAME=TaskManagerAgent
MEETING_ASSISTANT_AGENT_NAME=MeetingAssistantAgent
"""
        env_file.write_text(env_content)
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    # Initialize database
    print("🗄️ Initializing database...")
    try:
        from data_store.task_store import TaskStore
        store = TaskStore()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    
    print("\n🎉 Your On-Premises Multi-Agent Task Manager System is ready!")
    print("\n📋 Next steps:")
    print("1. Start the MCP server:     uv run mcp-server")
    print("2. Start Task Manager:       uv run task-manager")
    print("3. Start Meeting Assistant:  uv run meeting-assistant")
    print("\n📖 Or run the demo:         uv run python demo.py")
    print("\n📚 For more information, see the README.md file")
    
    return True


def main():
    """Main setup function."""
    try:
        success = setup_project()
        if success:
            print("\n🎯 Setup completed! You can now start using the system.")
        else:
            print("\n💥 Setup failed. Please check the error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Setup failed with unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 