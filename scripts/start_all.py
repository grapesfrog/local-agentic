#!/usr/bin/env python3
"""
Script to start all services in the On-Premises Multi-Agent Task Manager System.

This script will:
1. Check if Ollama is running
2. Start the MCP server
3. Start the A2A server
4. Start the Task Manager Agent
5. Start the Meeting Assistant Agent
6. Optionally start the ADK web interface

Usage:
    python scripts/start_all.py [--web] [--demo] [--stop-first]
"""

import os
import sys
import time
import subprocess
import threading
import argparse
import signal
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print(f"[INFO] Python executable: {sys.executable}")
print(f"[INFO] sys.prefix: {sys.prefix}")
print(f"[INFO] VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'not set')}")

def check_ollama():
    """Check if Ollama is running."""
    print("🔍 Checking Ollama...")
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  ✓ Ollama is running")
            return True
        else:
            print("  ✗ Ollama is not running")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ✗ Ollama not found or not responding")
        return False

def check_port(port):
    """Check if a port is available."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def wait_for_service(url, timeout=30, expected_status=200):
    """Wait for a service to be available."""
    print(f"  Waiting for service at {url} ...")
    for i in range(timeout):
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == expected_status:
                print(f"    ✓ Service at {url} is up!")
                return True
        except Exception:
            pass
        if i % 5 == 0 and i > 0:  # Print progress every 5 seconds
            print(f"    ... still waiting ({i+1}/{timeout}s)")
        time.sleep(1)
    print(f"    ✗ Service at {url} did not respond in time.")
    return False

def start_mcp_server():
    """Start the MCP server."""
    print("🚀 Starting MCP Server...")
    
    if not check_port(8002):
        print("  ✗ Port 8002 is already in use")
        return None
    
    try:
        # Set environment variable for port
        env = os.environ.copy()
        env['MCP_SERVER_PORT'] = '8002'
        
        process = subprocess.Popen(
            ['uv', 'run', 'python', 'mcp_server/task_mcp_server.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start and verify it's running
        time.sleep(3)
        if process.poll() is None:
            if wait_for_service("http://localhost:8002/health", timeout=30):
                print("  ✓ MCP Server started on port 8002")
                return process
            else:
                process.terminate()
                print("  ✗ MCP Server failed to respond to health check")
                return None
        else:
            stdout, stderr = process.communicate()
            print(f"  ✗ MCP Server failed to start: {stderr}")
            return None
            
    except Exception as e:
        print(f"  ✗ Error starting MCP Server: {e}")
        return None

def start_a2a_server():
    """Start the A2A server."""
    print("🔗 Starting A2A Server...")
    
    if not check_port(8001):
        print("  ✗ Port 8001 is already in use")
        return None
    
    try:
        process = subprocess.Popen(
            ['uv', 'run', 'python', 'start_a2a_server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start and verify it's running
        time.sleep(3)
        if process.poll() is None:
            if wait_for_service("http://localhost:8001/a2a/health", timeout=30):
                print("  ✓ A2A Server started on port 8001")
                return process
            else:
                process.terminate()
                print("  ✗ A2A Server failed to respond to health check")
                return None
        else:
            stdout, stderr = process.communicate()
            print(f"  ✗ A2A Server failed to start: {stderr}")
            return None
            
    except Exception as e:
        print(f"  ✗ Error starting A2A Server: {e}")
        return None

def start_task_manager():
    """Start the Task Manager Agent."""
    print("📋 Starting Task Manager Agent...")
    
    try:
        process = subprocess.Popen(
            ['uv', 'run', 'python', 'cli/task_manager_cli.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for agent to start
        time.sleep(3)
        
        if process.poll() is None:
            print("  ✓ Task Manager Agent started")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"  ✗ Task Manager Agent failed to start: {stderr}")
            return None
            
    except Exception as e:
        print(f"  ✗ Error starting Task Manager Agent: {e}")
        return None

def start_meeting_assistant():
    """Start the Meeting Assistant Agent."""
    print("🤖 Starting Meeting Assistant Agent...")
    
    try:
        process = subprocess.Popen(
            ['uv', 'run', 'python', 'cli/meeting_assistant_cli.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for agent to start
        time.sleep(2)
        
        if process.poll() is None:
            print("  ✓ Meeting Assistant Agent started")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"  ✗ Meeting Assistant Agent failed to start: {stderr}")
            return None
            
    except Exception as e:
        print(f"  ✗ Error starting Meeting Assistant Agent: {e}")
        return None

def start_adk_web():
    """Start the ADK web interface."""
    print("🌐 Starting ADK Web Interface...")
    
    if not check_port(8000):
        print("  ✗ Port 8000 is already in use")
        return None
    
    try:
        process = subprocess.Popen(
            ['uv', 'run', 'adk', 'web'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for web UI to start and verify it's running
        time.sleep(5)
        if process.poll() is None:
            if wait_for_service("http://localhost:8000", timeout=30):
                print("  ✓ ADK Web Interface started on port 8000")
                return process
            else:
                print("  ⚠️ ADK Web Interface started but not responding to health check")
                return process  # Don't fail, just warn
        else:
            stdout, stderr = process.communicate()
            print(f"  ✗ ADK Web Interface failed to start: {stderr}")
            return None
            
    except Exception as e:
        print(f"  ✗ Error starting ADK Web Interface: {e}")
        return None

def run_demo():
    """Run the demo script."""
    print("🎬 Running Demo...")
    
    try:
        process = subprocess.run(
            ['uv', 'run', 'python', 'scripts/run_demo.py'],
            timeout=300  # 5 minutes timeout
        )
        
        if process.returncode == 0:
            print("  ✓ Demo completed successfully")
        else:
            print("  ✗ Demo failed")
            
    except subprocess.TimeoutExpired:
        print("  ⏰ Demo timed out")
    except Exception as e:
        print(f"  ✗ Error running demo: {e}")

def monitor_processes(processes):
    """Monitor running processes and handle cleanup."""
    def signal_handler(signum, frame):
        print("\n🛑 Received interrupt signal. Stopping all services...")
        for name, process in processes:
            try:
                if process.poll() is None:  # Still running
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"  ✓ {name} stopped")
                else:
                    print(f"  - {name} already stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"  ⚠️ {name} force killed")
            except Exception as e:
                print(f"  ✗ Error stopping {name}: {e}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            time.sleep(1)
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️ {name} has stopped unexpectedly")
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

def main():
    """Main function to start all services."""
    parser = argparse.ArgumentParser(description="Start all services in the Multi-Agent Task Manager System")
    parser.add_argument("--web", action="store_true", help="Start the ADK web interface")
    parser.add_argument("--demo", action="store_true", help="Run the demo after starting services")
    parser.add_argument("--stop-first", action="store_true", help="Stop existing services before starting")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("On-Premises Multi-Agent Task Manager - Service Starter")
    print("=" * 70)
    
    # Check Ollama first
    if not check_ollama():
        print("❌ Ollama is required but not running. Please start Ollama first.")
        sys.exit(1)
    
    processes = []
    
    try:
        # Start MCP server
        mcp_process = start_mcp_server()
        if mcp_process:
            processes.append(("MCP Server", mcp_process))
        else:
            print("❌ Failed to start MCP Server. Exiting.")
            sys.exit(1)
        
        # Start A2A server
        a2a_process = start_a2a_server()
        if a2a_process:
            processes.append(("A2A Server", a2a_process))
        else:
            print("❌ Failed to start A2A Server. Exiting.")
            sys.exit(1)
        
        # Start Task Manager Agent
        task_manager_process = start_task_manager()
        if task_manager_process:
            processes.append(("Task Manager Agent", task_manager_process))
        else:
            print("❌ Failed to start Task Manager Agent. Exiting.")
            sys.exit(1)
        
        # Start Meeting Assistant Agent
        meeting_assistant_process = start_meeting_assistant()
        if meeting_assistant_process:
            processes.append(("Meeting Assistant Agent", meeting_assistant_process))
        else:
            print("❌ Failed to start Meeting Assistant Agent. Exiting.")
            sys.exit(1)
        
        # Start ADK Web UI if requested
        if args.web:
            adk_process = start_adk_web()
            if adk_process:
                processes.append(("ADK Web UI", adk_process))
        
        print("\n" + "=" * 70)
        print("✅ All services started successfully!")
        print("=" * 70)
        print("Services running:")
        print("  • MCP Server: http://localhost:8002")
        print("  • A2A Server: http://localhost:8001")
        print("  • Task Manager Agent: CLI interface")
        print("  • Meeting Assistant Agent: CLI interface")
        if args.web:
            print("  • ADK Web UI: http://localhost:8000")
        print("\nPress Ctrl+C to stop all services")
        
        # Run demo if requested
        if args.demo:
            print("\n" + "-" * 50)
            run_demo()
            print("-" * 50)
        
        # Monitor processes
        monitor_processes(processes)
        
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 