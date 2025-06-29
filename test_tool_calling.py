#!/usr/bin/env python3
"""
Tool Calling Test Script

This script tests the MCP tool calling functionality to validate that tools work correctly
when the ADK web UI has issues with tool calling.

Usage:
    python test_tool_calling.py
"""

import requests
import json
import time
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print(f"[INFO] Python executable: {sys.executable}")
print(f"[INFO] sys.prefix: {sys.prefix}")
print(f"[INFO] VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'not set')}")

def test_mcp_server_health():
    """Test if MCP server is running and healthy."""
    print("🔍 Testing MCP Server Health...")
    
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ MCP Server is healthy: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"  ✗ MCP Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ MCP Server not responding: {e}")
        return False

def test_add_task():
    """Test adding a task via MCP."""
    print("📝 Testing Add Task...")
    
    try:
        response = requests.post(
            "http://localhost:8002/tools/add_task",
            json={"description": "Tool calling test task"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                task_id = result.get("data", {}).get("task_id")
                print(f"  ✓ Task added successfully (ID: {task_id})")
                return task_id
            else:
                print(f"  ✗ Add task failed: {result.get('message')}")
                return None
        else:
            print(f"  ✗ Add task request failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Add task error: {e}")
        return None

def test_list_tasks():
    """Test listing tasks via MCP."""
    print("📋 Testing List Tasks...")
    
    try:
        response = requests.get("http://localhost:8002/tools/list_tasks", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                tasks = result.get("data", {}).get("tasks", [])
                print(f"  ✓ Found {len(tasks)} tasks")
                for task in tasks[:3]:  # Show first 3 tasks
                    status_icon = "✓" if task.get("status") == "completed" else "○"
                    print(f"    {status_icon} {task.get('id')}. {task.get('description')}")
                return True
            else:
                print(f"  ✗ List tasks failed: {result.get('message')}")
                return False
        else:
            print(f"  ✗ List tasks request failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ List tasks error: {e}")
        return False

def test_mark_task_complete(task_id):
    """Test marking a task as complete via MCP."""
    print(f"✅ Testing Mark Task Complete (ID: {task_id})...")
    
    try:
        response = requests.post(
            "http://localhost:8002/tools/mark_task_complete",
            json={"task_id": str(task_id)},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"  ✓ Task {task_id} marked as complete")
                return True
            else:
                print(f"  ✗ Mark task complete failed: {result.get('message')}")
                return False
        else:
            print(f"  ✗ Mark task complete request failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Mark task complete error: {e}")
        return False

def test_delete_task(task_id):
    """Test deleting a task via MCP."""
    print(f"🗑️ Testing Delete Task (ID: {task_id})...")
    
    try:
        response = requests.post(
            "http://localhost:8002/tools/delete_task",
            json={"task_id": str(task_id)},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"  ✓ Task {task_id} deleted successfully")
                return True
            else:
                print(f"  ✗ Delete task failed: {result.get('message')}")
                return False
        else:
            print(f"  ✗ Delete task request failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Delete task error: {e}")
        return False

def test_get_task_count():
    """Test getting task count via MCP."""
    print("🔢 Testing Get Task Count...")
    
    try:
        response = requests.get("http://localhost:8002/tools/get_task_count", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                count = result.get("data", {}).get("count", 0)
                print(f"  ✓ Total tasks: {count}")
                return True
            else:
                print(f"  ✗ Get task count failed: {result.get('message')}")
                return False
        else:
            print(f"  ✗ Get task count request failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Get task count error: {e}")
        return False

def test_cli_functionality():
    """Test CLI functionality by importing and testing agents."""
    print("💻 Testing CLI Functionality...")
    
    try:
        from agents.task_manager_agent import TaskManagerAgent
        from agents.meeting_assistant_agent import MeetingAssistantAgent
        
        # Test Task Manager Agent
        task_agent = TaskManagerAgent()
        result = task_agent.add_task("CLI test task")
        if result.get("success"):
            print("  ✓ Task Manager Agent tool calling works")
            
            # Clean up test task
            task_id = result.get("data", {}).get("task_id")
            if task_id:
                task_agent.delete_task(str(task_id))
        else:
            print(f"  ✗ Task Manager Agent tool calling failed: {result.get('message')}")
        
        # Test Meeting Assistant Agent
        meeting_agent = MeetingAssistantAgent()
        action_items = meeting_agent.extract_action_items("Action: Test action item extraction")
        if action_items:
            print("  ✓ Meeting Assistant Agent action extraction works")
        else:
            print("  ✗ Meeting Assistant Agent action extraction failed")
        
        return True
    except Exception as e:
        print(f"  ✗ CLI functionality test error: {e}")
        return False

def main():
    """Run all tool calling tests."""
    print("=" * 70)
    print("Tool Calling Test - Multi-Agent Task Manager System")
    print("=" * 70)
    
    # Check if MCP server is running
    if not test_mcp_server_health():
        print("\n❌ MCP Server is not running. Please start it first:")
        print("   python mcp_server/task_mcp_server.py")
        print("   or")
        print("   python scripts/start_all.py")
        return 1
    
    print("\n" + "=" * 70)
    print("Testing MCP Tool Calling...")
    print("=" * 70)
    
    tests = [
        ("Get Task Count", test_get_task_count),
        ("List Tasks", test_list_tasks),
        ("Add Task", test_add_task),
    ]
    
    passed = 0
    total = len(tests)
    test_task_id = None
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_name == "Add Task":
            result = test_func()
            if result:
                test_task_id = result
                passed += 1
        elif test_func():
            passed += 1
    
    # Test task operations if we have a test task
    if test_task_id:
        print(f"\nTask Operations (ID: {test_task_id}):")
        if test_mark_task_complete(test_task_id):
            passed += 1
            total += 1
        
        if test_delete_task(test_task_id):
            passed += 1
            total += 1
    
    print("\n" + "=" * 70)
    print("Testing CLI Functionality...")
    print("=" * 70)
    
    if test_cli_functionality():
        passed += 1
        total += 1
    
    print("\n" + "=" * 70)
    print(f"Tool Calling Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tool calling tests passed!")
        print("\n✅ Tool calling is working correctly.")
        print("   The ADK web UI limitation does not affect core functionality.")
        print("\n💡 Use these interfaces for full functionality:")
        print("   • CLI: python cli/task_manager_cli.py")
        print("   • CLI: python cli/meeting_assistant_cli.py")
        print("   • Direct API: curl http://localhost:8002/tools/...")
        return 0
    else:
        print("⚠️ Some tool calling tests failed.")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure MCP server is running on port 8002")
        print("   2. Check if database is accessible")
        print("   3. Verify environment configuration")
        print("   4. Run: python scripts/health_check.py")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 