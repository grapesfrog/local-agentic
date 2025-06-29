#!/usr/bin/env python3
"""
Demo script for the On-Premises Multi-Agent Task Manager System.

This script demonstrates the basic functionality of the system:
1. Starting the MCP server
2. Running the Task Manager Agent
3. Running the Meeting Assistant Agent
4. Demonstrating inter-agent communication

Usage:
    python demo.py
"""

import asyncio
import threading
import time
import logging
from mcp_server.task_mcp_server import TaskMCPServer
from agents.task_manager_agent import TaskManagerAgent
from agents.meeting_assistant_agent import MeetingAssistantAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def start_mcp_server():
    """Start the MCP server in a separate thread."""
    print("🚀 Starting MCP Server...")
    server = TaskMCPServer()
    server.run()


def start_task_manager():
    """Start the Task Manager Agent."""
    print("📋 Starting Task Manager Agent...")
    agent = TaskManagerAgent()
    
    # Start A2A server in background
    def run_a2a_server():
        agent.start_a2a_server()
    
    a2a_thread = threading.Thread(target=run_a2a_server, daemon=True)
    a2a_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Demonstrate basic task operations
    print("\n📝 Demonstrating Task Manager operations:")
    
    # Add some tasks
    result = agent.add_task("Submit weekly report")
    print(f"  ✓ {result.get('message')}")
    
    result = agent.add_task("Review budget figures")
    print(f"  ✓ {result.get('message')}")
    
    result = agent.add_task("Schedule team meeting")
    print(f"  ✓ {result.get('message')}")
    
    # List tasks
    result = agent.list_tasks()
    if result.get("success"):
        tasks = result.get("data", {}).get("tasks", [])
        print(f"\n📋 Current tasks ({len(tasks)}):")
        for task in tasks:
            status_icon = "✓" if task.get("status") == "completed" else "○"
            print(f"  {status_icon} {task.get('id')}. {task.get('description')}")
    
    return agent


async def demonstrate_meeting_assistant():
    """Demonstrate the Meeting Assistant Agent functionality."""
    print("\n🤖 Starting Meeting Assistant Agent...")
    agent = MeetingAssistantAgent()
    
    # Wait for A2A connection
    print("  Waiting for A2A connection...")
    time.sleep(3)
    
    # Demonstrate action item extraction
    print("\n📝 Demonstrating action item extraction:")
    meeting_notes = """
    Team Meeting - Q4 Planning
    
    Discussion points:
    - Budget review needed for Q4
    - New project timeline to be created
    - Client presentation needs updating
    
    Action: Email John about budget numbers
    Follow up: Schedule next meeting with Sarah
    TODO: Update project documentation
    Task: Review quarterly reports
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
        print(f"  ✗ {result.get('message')}")
    
    return agent


async def demonstrate_inter_agent_communication():
    """Demonstrate inter-agent communication."""
    print("\n🔗 Demonstrating inter-agent communication:")
    
    # Create agents
    task_agent = TaskManagerAgent()
    meeting_agent = MeetingAssistantAgent()
    
    # Process meeting notes that will delegate tasks via A2A
    meeting_notes = "Action: Prepare presentation slides. Follow up: Call client about requirements."
    
    print("  Meeting Assistant processing notes and delegating tasks...")
    result = await meeting_agent.process_meeting_notes(meeting_notes)
    
    if result.get("success"):
        print("  ✓ Meeting Assistant successfully processed notes")
        
        # Check if tasks were added
        time.sleep(1)  # Give time for A2A communication
        task_result = task_agent.list_tasks()
        if task_result.get("success"):
            tasks = task_result.get("data", {}).get("tasks", [])
            print(f"  ✓ Task Manager now has {len(tasks)} tasks")
    else:
        print(f"  ✗ {result.get('message')}")


def main():
    """Main demo function."""
    print("=" * 70)
    print("On-Premises Multi-Agent Task Manager System - Demo")
    print("=" * 70)
    
    try:
        # Start MCP server in background
        mcp_thread = threading.Thread(target=start_mcp_server, daemon=True)
        mcp_thread.start()
        
        # Wait for MCP server to start
        time.sleep(3)
        
        # Start Task Manager Agent
        task_agent = start_task_manager()
        
        # Demonstrate Meeting Assistant
        asyncio.run(demonstrate_meeting_assistant())
        
        # Demonstrate inter-agent communication
        asyncio.run(demonstrate_inter_agent_communication())
        
        print("\n" + "=" * 70)
        print("Demo completed successfully!")
        print("=" * 70)
        print("\nTo continue using the system:")
        print("1. Start the MCP server: python mcp_server/task_mcp_server.py")
        print("2. Start Task Manager: python cli/task_manager_cli.py")
        print("3. Start Meeting Assistant: python cli/meeting_assistant_cli.py")
        print("\nOr use the convenience scripts:")
        print("  uv run task-manager")
        print("  uv run meeting-assistant")
        print("  uv run mcp-server")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        logger.exception("Demo error")


if __name__ == "__main__":
    main() 