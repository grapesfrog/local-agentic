#!/usr/bin/env python3
"""
End-to-End Delegation Test Script

This script tests the full workflow:
- System startup (starts all services)
- Meeting Assistant LLM extraction
- Delegation via tool calling
- Verification via MCP server HTTP API
- Task completion and verification

Usage:
    uv run python test_end_to_end_delegation.py
"""

import requests
import time
import subprocess
import threading
import signal
import os
import sys
from pathlib import Path

print(f"[INFO] Python executable: {sys.executable}")
print(f"[INFO] sys.prefix: {sys.prefix}")
print(f"[INFO] VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'not set')}")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class ServiceManager:
    """Manages starting and stopping services for testing."""
    
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_mcp_server(self):
        """Start the MCP server."""
        print("🚀 Starting MCP Server...")
        try:
            process = subprocess.Popen(
                ['uv', 'run', 'python', 'mcp_server/task_mcp_server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(('MCP Server', process))
            time.sleep(3)  # Wait for server to start
            return process
        except Exception as e:
            print(f"  ✗ Error starting MCP Server: {e}")
            return None
    
    def start_a2a_server(self):
        """Start the A2A server."""
        print("🔗 Starting A2A Server...")
        try:
            process = subprocess.Popen(
                ['uv', 'run', 'python', 'start_a2a_server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(('A2A Server', process))
            time.sleep(3)  # Wait for server to start
            return process
        except Exception as e:
            print(f"  ✗ Error starting A2A Server: {e}")
            return None
    
    def start_task_manager_agent(self):
        """Start the Task Manager Agent."""
        print("📋 Starting Task Manager Agent...")
        try:
            process = subprocess.Popen(
                ['uv', 'run', 'python', 'cli/task_manager_cli.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(('Task Manager Agent', process))
            time.sleep(2)  # Wait for agent to start
            return process
        except Exception as e:
            print(f"  ✗ Error starting Task Manager Agent: {e}")
            return None
    
    def start_meeting_assistant_agent(self):
        """Start the Meeting Assistant Agent."""
        print("🤖 Starting Meeting Assistant Agent...")
        try:
            process = subprocess.Popen(
                ['uv', 'run', 'python', 'cli/meeting_assistant_cli.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(('Meeting Assistant Agent', process))
            time.sleep(2)  # Wait for agent to start
            return process
        except Exception as e:
            print(f"  ✗ Error starting Meeting Assistant Agent: {e}")
            return None
    
    def start_adk_web(self):
        """Start the ADK web interface."""
        print("🌐 Starting ADK Web Interface...")
        try:
            process = subprocess.Popen(
                ['uv', 'run', 'adk', 'web'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(('ADK Web UI', process))
            time.sleep(5)  # Wait for web UI to start
            return process
        except Exception as e:
            print(f"  ✗ Error starting ADK Web Interface: {e}")
            return None
    
    def stop_all(self):
        """Stop all running processes."""
        print("\n🛑 Stopping all services...")
        for name, process in self.processes:
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

def wait_for_service(url, timeout=30, expected_status=200):
    """Wait for a service to be available."""
    print(f"Waiting for service at {url} ...")
    for i in range(timeout):
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == expected_status:
                print(f"  ✓ Service at {url} is up!")
                return True
        except Exception:
            pass
        if i % 5 == 0:  # Print progress every 5 seconds
            print(f"  ... still waiting ({i+1}/{timeout}s)")
        time.sleep(1)
    print(f"  ✗ Service at {url} did not respond in time.")
    return False

def list_tasks():
    """List tasks via MCP server."""
    r = requests.get("http://localhost:8002/tools/list_tasks", timeout=5)
    if r.status_code == 200:
        return r.json().get("tasks", [])
    return []

def mark_task_complete(task_id):
    """Mark a task as complete via MCP server."""
    r = requests.post("http://localhost:8002/tools/mark_task_complete", 
                     json={"task_id": str(task_id)}, timeout=5)
    return r.status_code == 200 and r.json().get("success")

def get_task(task_id):
    """Get a specific task via MCP server."""
    r = requests.get(f"http://localhost:8002/tools/get_task/{task_id}", timeout=5)
    if r.status_code == 200:
        return r.json().get("task")
    return None

def main():
    print("=" * 80)
    print("End-to-End Delegation Test - Multi-Agent Task Manager System")
    print("=" * 80)
    
    service_manager = ServiceManager()
    
    try:
        # 1. Start all services
        print("\n🔧 Starting all services...")
        
        # Start MCP server
        if not service_manager.start_mcp_server():
            print("❌ Failed to start MCP server. Exiting.")
            return 1
        
        # Start A2A server
        if not service_manager.start_a2a_server():
            print("❌ Failed to start A2A server. Exiting.")
            return 1
        
        # Start Task Manager Agent
        if not service_manager.start_task_manager_agent():
            print("❌ Failed to start Task Manager Agent. Exiting.")
            return 1
        
        # Start Meeting Assistant Agent
        if not service_manager.start_meeting_assistant_agent():
            print("❌ Failed to start Meeting Assistant Agent. Exiting.")
            return 1
        
        # Start ADK Web UI
        service_manager.start_adk_web()  # Optional, don't fail if it doesn't start
        
        # 2. Wait for services to be ready
        print("\n⏳ Waiting for services to be ready...")
        
        # Wait for MCP server
        if not wait_for_service("http://localhost:8002/health", timeout=30):
            print("❌ MCP server not available. Exiting.")
            return 1
        
        # Wait for A2A server
        if not wait_for_service("http://localhost:8001/a2a/health", timeout=30):
            print("❌ A2A server not available. Exiting.")
            return 1
        
        # Wait for ADK Web UI (optional)
        wait_for_service("http://localhost:8000", timeout=10, expected_status=200)
        
        # 3. List tasks before delegation
        tasks_before = list_tasks()
        print(f"\n📊 Tasks before delegation: {len(tasks_before)}")

        # 4. Use Meeting Assistant to process notes and delegate tasks
        from agents.meeting_assistant_agent import MeetingAssistantAgent
        meeting_agent = MeetingAssistantAgent()
        meeting_notes = """
        Project Sync Meeting:
        Action: Prepare project update slides
        TODO: Email client about next steps
        Follow up: Schedule design review
        """
        print("\n🔄 Processing meeting notes and delegating tasks...")
        result = meeting_agent.process_meeting_notes(meeting_notes)
        if hasattr(result, "__await__"):
            # If coroutine, run it
            import asyncio
            result = asyncio.run(result)
        if not result.get("success"):
            print(f"❌ Failed to process meeting notes: {result.get('message')}")
            return 1
        print(f"  ✓ Delegation result: {result.get('data', {}).get('delegation_result', {})}")

        # 5. Wait for delegation to propagate
        time.sleep(2)

        # 6. List tasks after delegation
        tasks_after = list_tasks()
        print(f"📊 Tasks after delegation: {len(tasks_after)}")
        if len(tasks_after) <= len(tasks_before):
            print("❌ No new tasks were delegated!")
            return 1
        print("  ✓ Tasks were delegated!")

        # 7. Mark the first new task as complete
        new_tasks = [t for t in tasks_after if t not in tasks_before]
        if not new_tasks:
            new_tasks = tasks_after[-3:]  # fallback: last 3 tasks
        task_to_complete = new_tasks[0]
        print(f"✅ Marking task as complete: {task_to_complete['id']} - {task_to_complete['description']}")
        if not mark_task_complete(task_to_complete['id']):
            print("❌ Failed to mark task as complete!")
            return 1
        print("  ✓ Task marked as complete!")

        # 8. Verify task status
        completed_task = get_task(task_to_complete['id'])
        if completed_task and completed_task.get("status") == "completed":
            print(f"  ✓ Task status is 'completed' as expected!")
            print("\n🎉 End-to-end delegation test PASSED!")
            return 0
        else:
            print(f"❌ Task status is not 'completed': {completed_task}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1
    finally:
        # Always stop all services
        service_manager.stop_all()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 