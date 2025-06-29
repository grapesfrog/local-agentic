#!/usr/bin/env python3
"""Test script to verify Task Manager agent tools work correctly."""

from task_manager_agent.agent import list_tasks_tool, add_task_tool

def test_task_manager_tools():
    """Test the Task Manager agent tools."""
    print("Testing Task Manager agent tools...")
    
    # Test listing tasks
    print("\n1. Testing list_tasks_tool:")
    try:
        result = list_tasks_tool()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test adding a task
    print("\n2. Testing add_task_tool:")
    try:
        result = add_task_tool("Test task from direct tool call")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test listing tasks again
    print("\n3. Testing list_tasks_tool again:")
    try:
        result = list_tasks_tool()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_task_manager_tools() 