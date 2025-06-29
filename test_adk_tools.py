#!/usr/bin/env python3
"""
Test script to verify Task Manager agent tools work correctly
"""

from task_manager_agent.agent import list_tasks_tool, add_task_tool

def test_tools():
    print("Testing Task Manager Agent Tools...")
    print("=" * 50)
    
    # Test adding a task
    print("1. Adding a test task...")
    result = add_task_tool("Test task from ADK tools test")
    print(f"Result: {result}")
    print()
    
    # Test listing tasks
    print("2. Listing all tasks...")
    result = list_tasks_tool()
    print(f"Result:\n{result}")
    print()
    
    print("Tool test completed!")

if __name__ == "__main__":
    test_tools() 