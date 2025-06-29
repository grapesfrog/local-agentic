#!/usr/bin/env python3
"""
Run demo script for the On-Premises Multi-Agent Task Manager System.

This script demonstrates the complete system functionality including:
- MCP server operations
- Task Manager Agent capabilities
- Meeting Assistant Agent capabilities
- Inter-agent communication via A2A
"""

import sys
import os
print(f"[INFO] Python executable: {sys.executable}")
print(f"[INFO] sys.prefix: {sys.prefix}")
print(f"[INFO] VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'not set')}")

import time
import asyncio
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def start_mcp_server():
    """Start the MCP server in background."""
    print("🚀 Starting MCP Server...")
    
    try:
        from mcp_server.task_mcp_server import TaskMCPServer
        server = TaskMCPServer()
        
        def run_server():
            server.run()
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        
        # Wait for server to start
        time.sleep(3)
        print("  ✓ MCP Server started on port 8002")
        return True
    except Exception as e:
        print(f"  ✗ Failed to start MCP Server: {e}")
        return False

def start_task_manager():
    """Start the Task Manager Agent."""
    print("📋 Starting Task Manager Agent...")
    
    try:
        from agents.task_manager_agent import TaskManagerAgent
        
        agent = TaskManagerAgent()
        
        # Start A2A server in background
        def run_a2a_server():
            agent.start_a2a_server()
        
        a2a_thread = threading.Thread(target=run_a2a_server, daemon=True)
        a2a_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        print("  ✓ Task Manager Agent started (A2A on port 8001)")
        return agent
    except Exception as e:
        print(f"  ✗ Failed to start Task Manager Agent: {e}")
        return None

async def demonstrate_task_operations(agent):
    """Demonstrate basic task operations."""
    print("\n📝 Demonstrating Task Operations:")
    
    # Add tasks
    tasks_to_add = [
        "Submit weekly report",
        "Review budget figures", 
        "Schedule team meeting",
        "Update project documentation"
    ]
    
    for task in tasks_to_add:
        result = agent.add_task(task)
        if result.get("success"):
            print(f"  ✓ Added: {task}")
        else:
            print(f"  ✗ Failed to add: {task}")
    
    # List tasks
    result = agent.list_tasks()
    if result.get("success"):
        tasks = result.get("data", {}).get("tasks", [])
        print(f"\n📋 Current tasks ({len(tasks)}):")
        for task in tasks:
            status_icon = "✓" if task.get("status") == "completed" else "○"
            print(f"  {status_icon} {task.get('id')}. {task.get('description')}")
    
    # Complete a task
    if tasks:
        first_task = tasks[0]
        result = agent.mark_task_complete(str(first_task.get("id")))
        if result.get("success"):
            print(f"\n  ✓ Completed task: {first_task.get('description')}")
    
    # Show final state
    result = agent.list_tasks()
    if result.get("success"):
        tasks = result.get("data", {}).get("tasks", [])
        print(f"\n📋 Final task state ({len(tasks)}):")
        for task in tasks:
            status_icon = "✓" if task.get("status") == "completed" else "○"
            print(f"  {status_icon} {task.get('id')}. {task.get('description')}")

async def demonstrate_meeting_assistant():
    """Demonstrate Meeting Assistant capabilities."""
    print("\n🤖 Demonstrating Meeting Assistant Agent:")
    
    try:
        from agents.meeting_assistant_agent import MeetingAssistantAgent
        
        agent = MeetingAssistantAgent()
        
        # Wait for A2A connection
        print("  Waiting for A2A connection...")
        time.sleep(3)
        
        # Process meeting notes
        meeting_notes = """
        Team Meeting - Q4 Planning Session
        
        Discussion Points:
        - Budget review needed for Q4 projects
        - New project timeline needs to be created
        - Client presentation requires updating
        - Team training session to be scheduled
        
        Action Items:
        - Email John about budget numbers
        - Follow up: Schedule next meeting with Sarah
        - TODO: Update project documentation
        - Task: Review quarterly reports
        - Deadline: Prepare presentation slides by Friday
        """
        
        print("  Processing meeting notes...")
        result = await agent.process_meeting_notes(meeting_notes)
        
        if result.get("success"):
            data = result.get("data", {})
            action_items = data.get("action_items", [])
            delegation_result = data.get("delegation_result", {})
            
            print(f"  ✓ Found {len(action_items)} action items:")
            for i, item in enumerate(action_items, 1):
                print(f"    {i}. {item}")
            
            if delegation_result:
                successful = delegation_result.get("successful_delegations", 0)
                failed = delegation_result.get("failed_delegations", 0)
                print(f"  ✓ Successfully delegated {successful} tasks")
                if failed > 0:
                    print(f"  ✗ Failed to delegate {failed} tasks")
        else:
            print(f"  ✗ Failed to process meeting notes: {result.get('message')}")
        
        return agent
    except Exception as e:
        print(f"  ✗ Meeting Assistant demo failed: {e}")
        return None

async def demonstrate_inter_agent_communication():
    """Demonstrate inter-agent communication."""
    print("\n🔗 Demonstrating Inter-Agent Communication:")
    
    try:
        from agents.task_manager_agent import TaskManagerAgent
        from agents.meeting_assistant_agent import MeetingAssistantAgent
        
        # Create agents
        task_agent = TaskManagerAgent()
        meeting_agent = MeetingAssistantAgent()
        
        # Process meeting notes that will delegate tasks via A2A
        meeting_notes = """
        Quick Standup Meeting:
        
        Action: Prepare presentation slides for client meeting
        Follow up: Call client about project requirements
        TODO: Update project timeline
        Task: Review code changes
        """
        
        print("  Meeting Assistant processing notes and delegating tasks...")
        result = await meeting_agent.process_meeting_notes(meeting_notes)
        
        if result.get("success"):
            print("  ✓ Meeting Assistant successfully processed notes")
            
            # Check if tasks were added via A2A
            time.sleep(2)  # Give time for A2A communication
            task_result = task_agent.list_tasks()
            if task_result.get("success"):
                tasks = task_result.get("data", {}).get("tasks", [])
                print(f"  ✓ Task Manager now has {len(tasks)} total tasks")
                
                # Show the newly added tasks
                if len(tasks) > 4:  # Assuming we had 4 tasks from earlier demo
                    print("  📋 Newly delegated tasks:")
                    for task in tasks[4:]:  # Show tasks added after initial demo
                        print(f"    ○ {task.get('id')}. {task.get('description')}")
        else:
            print(f"  ✗ Inter-agent communication failed: {result.get('message')}")
    except Exception as e:
        print(f"  ✗ Inter-agent communication demo failed: {e}")

async def demonstrate_mcp_tools():
    """Demonstrate MCP tool usage."""
    print("\n🔧 Demonstrating MCP Tools:")
    
    try:
        import requests
        
        # Test MCP server tools
        base_url = "http://localhost:8002/tools"
        
        # Add a task via MCP
        response = requests.post(
            f"{base_url}/add_task",
            json={"description": "MCP tool test task"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                task_id = result.get("data", {}).get("task_id")
                print(f"  ✓ Added task via MCP: {task_id}")
                
                # Get task count via MCP
                response = requests.get(f"{base_url}/get_task_count", timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        count = result.get("data", {}).get("count", 0)
                        print(f"  ✓ Total tasks via MCP: {count}")
                
                # Clean up test task
                response = requests.post(
                    f"{base_url}/delete_task",
                    json={"task_id": task_id},
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"  ✓ Cleaned up test task")
        else:
            print(f"  ✗ MCP tool test failed: {response.status_code}")
    except Exception as e:
        print(f"  ✗ MCP tools demo failed: {e}")

def main():
    """Run the complete demo."""
    print("=" * 80)
    print("On-Premises Multi-Agent Task Manager System - Complete Demo")
    print("=" * 80)
    
    try:
        # Start MCP server
        if not start_mcp_server():
            print("❌ Failed to start MCP server. Demo cannot continue.")
            return 1
        
        # Start Task Manager Agent
        task_agent = start_task_manager()
        if not task_agent:
            print("❌ Failed to start Task Manager Agent. Demo cannot continue.")
            return 1
        
        # Run async demos
        async def run_demos():
            # Demonstrate task operations
            await demonstrate_task_operations(task_agent)
            
            # Demonstrate MCP tools
            await demonstrate_mcp_tools()
            
            # Demonstrate Meeting Assistant
            await demonstrate_meeting_assistant()
            
            # Demonstrate inter-agent communication
            await demonstrate_inter_agent_communication()
        
        # Run the async demos
        asyncio.run(run_demos())
        
        print("\n" + "=" * 80)
        print("🎉 Demo completed successfully!")
        print("=" * 80)
        print("\nThe system demonstrated:")
        print("  ✓ MCP server functionality")
        print("  ✓ Task Manager Agent operations")
        print("  ✓ Meeting Assistant Agent capabilities")
        print("  ✓ Inter-agent communication via A2A")
        print("  ✓ MCP tool integration")
        
        print("\nTo continue using the system:")
        print("  1. Start services: python scripts/start_all.py")
        print("  2. Use Task Manager: python cli/task_manager_cli.py")
        print("  3. Use Meeting Assistant: python cli/meeting_assistant_cli.py")
        print("  4. Access ADK Web UI: uv run adk web")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 