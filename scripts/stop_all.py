#!/usr/bin/env python3
"""
Stop all services script for the On-Premises Multi-Agent Task Manager System.

This script gracefully shuts down all running services and cleans up processes.
"""

import sys
import os
import signal
import subprocess
import time
import psutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print(f"[INFO] Python executable: {sys.executable}")
print(f"[INFO] sys.prefix: {sys.prefix}")
print(f"[INFO] VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'not set')}")

def find_processes_by_port(port):
    """Find processes using a specific port."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            connections = proc.connections()
            for conn in connections:
                if conn.laddr.port == port:
                    processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def find_python_processes_by_name(name_pattern):
    """Find Python processes by name pattern."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if name_pattern.lower() in cmdline.lower():
                    processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def stop_process(proc, service_name):
    """Stop a process gracefully."""
    try:
        print(f"  Stopping {service_name} (PID: {proc.pid})...")
        
        # Try graceful shutdown first
        proc.terminate()
        
        # Wait for graceful shutdown
        try:
            proc.wait(timeout=5)
            print(f"  ✓ {service_name} stopped gracefully")
            return True
        except psutil.TimeoutExpired:
            # Force kill if graceful shutdown fails
            print(f"  Force killing {service_name}...")
            proc.kill()
            proc.wait(timeout=2)
            print(f"  ✓ {service_name} force stopped")
            return True
            
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        print(f"  ⚠️ Could not stop {service_name}: {e}")
        return False

def stop_mcp_server():
    """Stop MCP server."""
    print("🔍 Stopping MCP Server...")
    
    # Find processes on port 8002
    processes = find_processes_by_port(8002)
    
    if not processes:
        print("  ✓ MCP Server is not running")
        return True
    
    success = True
    for proc in processes:
        if not stop_process(proc, "MCP Server"):
            success = False
    
    return success

def stop_a2a_server():
    """Stop A2A server."""
    print("🔗 Stopping A2A Server...")
    
    # Find processes on port 8001
    processes = find_processes_by_port(8001)
    
    if not processes:
        print("  ✓ A2A Server is not running")
        return True
    
    success = True
    for proc in processes:
        if not stop_process(proc, "A2A Server"):
            success = False
    
    return success

def stop_task_manager():
    """Stop Task Manager Agent."""
    print("📋 Stopping Task Manager Agent...")
    
    # Find task manager processes
    processes = find_python_processes_by_name("task_manager_cli")
    
    if not processes:
        print("  ✓ Task Manager Agent is not running")
        return True
    
    success = True
    for proc in processes:
        if not stop_process(proc, "Task Manager Agent"):
            success = False
    
    return success

def stop_meeting_assistant():
    """Stop Meeting Assistant Agent."""
    print("🤖 Stopping Meeting Assistant Agent...")
    
    # Find meeting assistant processes
    processes = find_python_processes_by_name("meeting_assistant_cli")
    
    if not processes:
        print("  ✓ Meeting Assistant Agent is not running")
        return True
    
    success = True
    for proc in processes:
        if not stop_process(proc, "Meeting Assistant Agent"):
            success = False
    
    return True

def stop_adk_web():
    """Stop ADK Web Interface."""
    print("🌐 Stopping ADK Web Interface...")
    
    # Find processes on port 8000
    processes = find_processes_by_port(8000)
    
    if not processes:
        print("  ✓ ADK Web Interface is not running")
        return True
    
    success = True
    for proc in processes:
        if not stop_process(proc, "ADK Web Interface"):
            success = False
    
    return success

def stop_ollama():
    """Stop Ollama (optional)."""
    print("🤖 Checking Ollama...")
    
    try:
        # Check if Ollama is running
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("  Ollama is running (will continue running)")
            print("  To stop Ollama manually: ollama serve --stop")
            return True
        else:
            print("  ✓ Ollama is not running")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ✓ Ollama is not running")
        return True

def cleanup_temp_files():
    """Clean up temporary files."""
    print("🧹 Cleaning up temporary files...")
    
    try:
        # Remove any temporary files created during operation
        temp_patterns = [
            "*.tmp",
            "*.log",
            "__pycache__",
            "*.pyc"
        ]
        
        cleaned = 0
        for pattern in temp_patterns:
            for file_path in Path(".").rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        cleaned += 1
                    elif file_path.is_dir():
                        import shutil
                        shutil.rmtree(file_path)
                        cleaned += 1
                except Exception:
                    pass
        
        if cleaned > 0:
            print(f"  ✓ Cleaned up {cleaned} temporary files")
        else:
            print("  ✓ No temporary files to clean")
        
        return True
    except Exception as e:
        print(f"  ⚠️ Cleanup error: {e}")
        return False

def verify_ports_available():
    """Verify that all ports are now available."""
    print("🔍 Verifying ports are available...")
    
    ports_to_check = [8000, 8001, 8002]
    all_available = True
    
    for port in ports_to_check:
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                print(f"  ✓ Port {port} is available")
        except OSError:
            print(f"  ⚠️ Port {port} is still in use")
            all_available = False
    
    return all_available

def main():
    """Stop all services and clean up."""
    print("=" * 60)
    print("Stop All Services - Multi-Agent Task Manager System")
    print("=" * 60)
    
    try:
        # Stop all services
        services = [
            ("ADK Web Interface", stop_adk_web),
            ("Meeting Assistant Agent", stop_meeting_assistant),
            ("Task Manager Agent", stop_task_manager),
            ("A2A Server", stop_a2a_server),
            ("MCP Server", stop_mcp_server),
        ]
        
        all_stopped = True
        for service_name, stop_func in services:
            print(f"\n{service_name}:")
            if not stop_func():
                all_stopped = False
        
        # Check Ollama (but don't stop it)
        print(f"\nOllama:")
        stop_ollama()
        
        # Clean up
        print(f"\nCleanup:")
        cleanup_temp_files()
        
        # Verify ports
        print(f"\nVerification:")
        verify_ports_available()
        
        print("\n" + "=" * 60)
        if all_stopped:
            print("🎉 All services stopped successfully!")
        else:
            print("⚠️ Some services may still be running")
        
        print("\nTo restart services:")
        print("  python scripts/start_all.py")
        print("\nTo start individual services:")
        print("  python mcp_server/task_mcp_server.py")
        print("  python cli/task_manager_cli.py")
        print("  python cli/meeting_assistant_cli.py")
        print("  uv run adk web")
        
        return 0 if all_stopped else 1
        
    except KeyboardInterrupt:
        print("\n\nStop operation interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nStop operation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 