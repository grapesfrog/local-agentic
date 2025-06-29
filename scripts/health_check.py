#!/usr/bin/env python3
"""
Health Check Script for On-Premises Multi-Agent Task Manager System

This script checks the health of all system components:
- Environment configuration
- Dependencies
- Data directory and database
- Ollama
- MCP Server
- A2A Server
- Task Manager Agent
- Meeting Assistant Agent

Usage:
    uv run python scripts/health_check.py
"""

import os
import sys
import requests
import subprocess
import sqlite3
from pathlib import Path

print(f"[INFO] Python executable: {sys.executable}")
print(f"[INFO] sys.prefix: {sys.prefix}")
print(f"[INFO] VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'not set')}")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check environment configuration."""
    print("⚙️ Checking Environment Configuration...")
    
    env_vars = {
        'MCP_SERVER_HOST': 'localhost',
        'MCP_SERVER_PORT': '8002',
        'A2A_SERVER_HOST': 'localhost',
        'A2A_SERVER_PORT': '8001',
        'DATABASE_PATH': './data/tasks.db'
    }
    
    all_good = True
    for var, expected in env_vars.items():
        value = os.environ.get(var, expected)
        if value == expected:
            print(f"  ✓ {var} = {value}")
        else:
            print(f"  ⚠️ {var} = {value} (expected: {expected})")
            all_good = False
    
    return all_good

def check_dependencies():
    """Check required dependencies."""
    print("📦 Checking Dependencies...")
    
    dependencies = [
        'aiohttp',
        'requests',
        'python-dotenv',
        'google-adk'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} (missing)")
            missing.append(dep)
    
    if missing:
        print(f"  ⚠️ Missing packages: {', '.join(missing)}")
        return False
    return True

def check_data_directory():
    """Check data directory and database."""
    print("📁 Checking Data Directory...")
    
    data_dir = Path("./data")
    db_path = data_dir / "tasks.db"
    
    if not data_dir.exists():
        print("  ✗ Data directory does not exist")
        return False
    
    print("  ✓ Data directory exists")
    
    if not db_path.exists():
        print("  ✗ Database file does not exist")
        return False
    
    size = db_path.stat().st_size
    print(f"  ✓ Database file exists ({size} bytes)")
    
    return True

def check_database():
    """Check database connectivity and structure."""
    print("🗄️ Checking Database...")
    
    try:
        conn = sqlite3.connect("./data/tasks.db")
        cursor = conn.cursor()
        
        # Check if tasks table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        if not cursor.fetchone():
            print("  ✗ Tasks table does not exist")
            return False
        
        # Count tasks
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        print(f"  ✓ Database is accessible (contains {task_count} tasks)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False

def check_ollama():
    """Check if Ollama is running."""
    print("🤖 Checking Ollama...")
    
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            model_count = len(lines) - 1  # Subtract header line
            print(f"  ✓ Ollama is running ({model_count} models available)")
            return True
        else:
            print("  ✗ Ollama is not running")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ✗ Ollama not found or not responding")
        return False

def check_mcp_server():
    """Check MCP server health."""
    print("🔍 Checking MCP Server...")
    
    try:
        # Check if server is running
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            print(f"  ✓ MCP Server is running on localhost:8002")
            print(f"  ✓ MCP Server health: {status}")
            return True
        else:
            print(f"  ✗ MCP Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ✗ MCP Server is not running")
        return False
    except Exception as e:
        print(f"  ✗ MCP Server error: {e}")
        return False

def check_a2a_server():
    """Check A2A server health."""
    print("🔗 Checking A2A Server...")
    
    try:
        # Check if server is running using the correct endpoint
        response = requests.get("http://localhost:8001/a2a/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            print(f"  ✓ A2A Server is running on localhost:8001")
            print(f"  ✓ A2A Server health: {status}")
            return True
        else:
            print(f"  ⚠️ A2A Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ✗ A2A Server is not running")
        return False
    except Exception as e:
        print(f"  ✗ A2A Server error: {e}")
        return False

def check_task_manager_agent():
    """Check Task Manager Agent health."""
    print("📋 Checking Task Manager Agent...")
    
    try:
        # Try to connect to the agent via A2A
        response = requests.get("http://localhost:8001/a2a/capabilities", timeout=5)
        if response.status_code == 200:
            data = response.json()
            capabilities = data.get('capabilities', [])
            print(f"  ✓ Task Manager Agent is accessible via A2A")
            print(f"  ✓ Available capabilities: {', '.join(capabilities)}")
            return True
        else:
            print(f"  ⚠️ Task Manager Agent A2A responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ✗ Task Manager Agent is not accessible via A2A")
        return False
    except Exception as e:
        print(f"  ✗ Task Manager Agent error: {e}")
        return False

def check_meeting_assistant_agent():
    """Check Meeting Assistant Agent health."""
    print("🤖 Checking Meeting Assistant Agent...")
    
    # Since the Meeting Assistant Agent doesn't expose a health endpoint,
    # we'll just check if the module can be imported
    try:
        from agents.meeting_assistant_agent import MeetingAssistantAgent
        agent = MeetingAssistantAgent()
        print("  ✓ Meeting Assistant Agent module is accessible")
        return True
    except Exception as e:
        print(f"  ✗ Meeting Assistant Agent error: {e}")
        return False

def main():
    """Main health check function."""
    print("=" * 70)
    print("Health Check - On-Premises Multi-Agent Task Manager System")
    print("=" * 70)
    
    checks = [
        ("Environment Configuration", check_environment),
        ("Dependencies", check_dependencies),
        ("Data Directory", check_data_directory),
        ("Database", check_database),
        ("Ollama", check_ollama),
        ("MCP Server", check_mcp_server),
        ("A2A Server", check_a2a_server),
        ("Task Manager Agent", check_task_manager_agent),
        ("Meeting Assistant Agent", check_meeting_assistant_agent),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Error during {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("Health Check Results")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All systems are healthy!")
        print("The system is ready for use.")
    elif passed >= total * 0.8:
        print("⚠️ Most systems are healthy. Some minor issues detected.")
        print("The system should work, but check the warnings above.")
    else:
        print("❌ Multiple systems have issues.")
        print("Please address the problems above before using the system.")
    
    # Show failed checks
    failed = [name for name, result in results if not result]
    if failed:
        print(f"\nFailed checks: {', '.join(failed)}")
    
    return 0 if passed >= total * 0.8 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 