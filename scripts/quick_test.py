#!/usr/bin/env python3
"""
Quick Test Script for On-Premises Multi-Agent Task Manager System

This script performs quick functionality tests:
- Starts all services if not running
- Tests MCP server tools
- Tests A2A communication
- Tests task delegation workflow

Usage:
    uv run python scripts/quick_test.py
"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path

print(f"[INFO] Python executable: {sys.executable}")
print(f"[INFO] sys.prefix: {sys.prefix}")
print(f"[INFO] VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'not set')}")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class ServiceManager:
    """Manages starting and stopping services for testing."""
    
    def __init__(self):
        self.processes = []
        
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

def test_mcp_server():
    """Test MCP server functionality."""
    print("\n🔍 Testing MCP Server...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("  ✓ MCP Server health check passed")
        else:
            print(f"  ✗ MCP Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ MCP Server health check error: {e}")
        return False
    
    # Test add task
    try:
        response = requests.post(
            "http://localhost:8002/tools/add_task",
            json={"description": "Quick test task"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                task_id = data.get("task_id")
                print(f"  ✓ MCP Server add task passed (ID: {task_id})")
            else:
                print(f"  ✗ MCP Server add task failed: {data.get('error')}")
                return False
        else:
            print(f"  ✗ MCP Server add task failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ MCP Server add task error: {e}")
        return False
    
    # Test list tasks
    try:
        response = requests.get("http://localhost:8002/tools/list_tasks", timeout=5)
        if response.status_code == 200:
            data = response.json()
            tasks = data.get("tasks", [])
            print(f"  ✓ MCP Server list tasks passed ({len(tasks)} tasks)")
        else:
            print(f"  ✗ MCP Server list tasks failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ MCP Server list tasks error: {e}")
        return False
    
    return True

def test_a2a_server():
    """Test A2A server functionality."""
    print("\n🔗 Testing A2A Server...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8001/a2a/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            print(f"  ✓ A2A Server health check passed ({status})")
        else:
            print(f"  ✗ A2A Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ A2A Server health check error: {e}")
        return False
    
    # Test capabilities endpoint
    try:
        response = requests.get("http://localhost:8001/a2a/capabilities", timeout=5)
        if response.status_code == 200:
            data = response.json()
            capabilities = data.get('capabilities', [])
            # Handle both string and dict capabilities
            if capabilities and isinstance(capabilities[0], dict):
                capability_names = [cap.get('name', str(cap)) for cap in capabilities]
            else:
                capability_names = capabilities
            print(f"  ✓ A2A Server capabilities: {', '.join(capability_names)}")
        else:
            print(f"  ✗ A2A Server capabilities failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ A2A Server capabilities error: {e}")
        return False
    
    return True

def test_task_delegation():
    """Test task delegation workflow."""
    print("\n🔄 Testing Task Delegation...")
    
    try:
        from agents.meeting_assistant_agent import MeetingAssistantAgent
        meeting_agent = MeetingAssistantAgent()
        
        meeting_notes = """
        Quick Test Meeting:
        Action: Test task delegation
        TODO: Verify system functionality
        """
        
        result = meeting_agent.process_meeting_notes(meeting_notes)
        if hasattr(result, "__await__"):
            # If coroutine, run it
            import asyncio
            result = asyncio.run(result)
        
        if result.get("success"):
            delegation_result = result.get('data', {}).get('delegation_result', {})
            delegated_count = delegation_result.get('successful_delegations', 0)
            print(f"  ✓ Task delegation passed ({delegated_count} tasks delegated)")
            return True
        else:
            print(f"  ✗ Task delegation failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"  ✗ Task delegation error: {e}")
        return False

def main():
    """Main quick test function."""
    print("=" * 70)
    print("Quick Test - On-Premises Multi-Agent Task Manager System")
    print("=" * 70)
    
    service_manager = ServiceManager()
    
    try:
        # Check if services are already running
        print("\n🔍 Checking if services are already running...")
        
        mcp_running = False
        a2a_running = False
        
        try:
            response = requests.get("http://localhost:8002/health", timeout=2)
            if response.status_code == 200:
                print("  ✓ MCP Server is already running")
                mcp_running = True
        except:
            pass
        
        try:
            response = requests.get("http://localhost:8001/a2a/health", timeout=2)
            if response.status_code == 200:
                print("  ✓ A2A Server is already running")
                a2a_running = True
        except:
            pass
        
        # Start services if not running
        if not mcp_running:
            if not service_manager.start_mcp_server():
                print("❌ Failed to start MCP server. Exiting.")
                return 1
        
        if not a2a_running:
            if not service_manager.start_a2a_server():
                print("❌ Failed to start A2A server. Exiting.")
                return 1
        
        # Wait for services to be ready
        print("\n⏳ Waiting for services to be ready...")
        
        if not mcp_running:
            if not wait_for_service("http://localhost:8002/health", timeout=30):
                print("❌ MCP server not available. Exiting.")
                return 1
        
        if not a2a_running:
            if not wait_for_service("http://localhost:8001/a2a/health", timeout=30):
                print("❌ A2A server not available. Exiting.")
                return 1
        
        # Run tests
        tests = [
            ("MCP Server", test_mcp_server),
            ("A2A Server", test_a2a_server),
            ("Task Delegation", test_task_delegation),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append((name, result))
            except Exception as e:
                print(f"  ✗ {name} test error: {e}")
                results.append((name, False))
        
        # Summary
        print("\n" + "=" * 70)
        print("Quick Test Results")
        print("=" * 70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"Overall: {passed}/{total} tests passed")
        
        for name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {status} {name}")
        
        if passed == total:
            print("\n🎉 All quick tests passed!")
            print("The system is working correctly.")
            return 0
        else:
            print(f"\n⚠️ {total - passed} test(s) failed.")
            print("Check the errors above for details.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1
    finally:
        # Only stop services if we started them
        if service_manager.processes:
            service_manager.stop_all()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 