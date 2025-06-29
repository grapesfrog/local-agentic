#!/usr/bin/env python3
"""
Task Delegation Test Script

This script tests the task delegation functionality between the Meeting Assistant Agent
and Task Manager Agent via A2A (Agent-to-Agent) communication.

Usage:
    uv run python test_task_delegation.py
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print(f"[INFO] Python executable: {sys.executable}")
print(f"[INFO] sys.prefix: {sys.prefix}")
print(f"[INFO] VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'not set')}")

async def test_meeting_assistant_to_task_manager_delegation():
    """Test task delegation from Meeting Assistant to Task Manager via A2A."""
    print("🤖 Testing Meeting Assistant → Task Manager Delegation")
    print("=" * 60)
    
    try:
        from agents.meeting_assistant_agent import MeetingAssistantAgent
        from agents.task_manager_agent import TaskManagerAgent
        
        # Initialize agents
        meeting_agent = MeetingAssistantAgent()
        task_agent = TaskManagerAgent()
        
        # Get initial task count
        initial_count_result = task_agent.get_task_count()
        if initial_count_result.get("success"):
            initial_count = initial_count_result.get("data", {}).get("count", 0)
        else:
            print(f"⚠️ Could not get initial task count: {initial_count_result.get('message')}")
            initial_count = 0
        print(f"📊 Initial task count: {initial_count}")
        
        # Test meeting notes with action items
        meeting_notes = """
        Team Standup Meeting - June 29, 2025
        
        Discussion:
        - Project timeline needs updating
        - Client presentation requires preparation
        - Budget review is overdue
        
        Action Items:
        - Action: Update project timeline by end of day
        - Follow up: Prepare client presentation slides
        - TODO: Review quarterly budget numbers
        - Task: Schedule team training session
        - Deadline: Submit weekly report by Friday
        """
        
        print("\n📝 Processing meeting notes...")
        print(f"Meeting notes: {meeting_notes.strip()}")
        
        # Process meeting notes (this should delegate tasks via A2A)
        result = await meeting_agent.process_meeting_notes(meeting_notes)
        
        if result.get("success"):
            data = result.get("data", {})
            action_items = data.get("action_items", [])
            delegation_result = data.get("delegation_result", {})
            
            print(f"\n✅ Found {len(action_items)} action items:")
            for i, item in enumerate(action_items, 1):
                print(f"  {i}. {item}")
            
            if delegation_result:
                successful = delegation_result.get("successful_delegations", 0)
                failed = delegation_result.get("failed_delegations", 0)
                print(f"\n📤 Delegation Results:")
                print(f"  ✓ Successfully delegated: {successful} tasks")
                if failed > 0:
                    print(f"  ✗ Failed to delegate: {failed} tasks")
                
                # Wait a moment for A2A communication to complete
                time.sleep(2)
                
                # Check if tasks were actually added to Task Manager
                final_count_result = task_agent.get_task_count()
                if final_count_result.get("success"):
                    final_count = final_count_result.get("data", {}).get("count", 0)
                    tasks_added = final_count - initial_count
                    
                    print(f"\n📊 Task Count After Delegation:")
                    print(f"  Initial: {initial_count}")
                    print(f"  Final: {final_count}")
                    print(f"  Tasks Added: {tasks_added}")
                    
                    if tasks_added > 0:
                        print(f"✅ Task delegation successful! {tasks_added} tasks added via A2A")
                        
                        # List the newly added tasks
                        task_result = task_agent.list_tasks()
                        if task_result.get("success"):
                            tasks = task_result.get("data", {}).get("tasks", [])
                            print(f"\n📋 Current Tasks ({len(tasks)}):")
                            for task in tasks:
                                status_icon = "✓" if task.get("status") == "completed" else "○"
                                print(f"  {status_icon} {task.get('id')}. {task.get('description')}")
                        
                        return True
                    else:
                        print("❌ Task delegation failed - no tasks were added")
                        return False
                else:
                    print(f"❌ Could not get final task count: {final_count_result.get('message')}")
                    return False
            else:
                print("❌ No delegation result received")
                return False
        else:
            print(f"❌ Failed to process meeting notes: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Task delegation test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_direct_a2a_communication():
    """Test direct A2A communication between agents."""
    print("\n🔗 Testing Direct A2A Communication")
    print("=" * 60)
    
    try:
        from agents.meeting_assistant_agent import MeetingAssistantAgent
        from agents.task_manager_agent import TaskManagerAgent
        
        # Initialize agents
        meeting_agent = MeetingAssistantAgent()
        task_agent = TaskManagerAgent()
        
        # Test direct task addition via A2A
        print("📤 Testing direct task addition via A2A...")
        
        # Use the Meeting Assistant's A2A client with proper async context manager
        async with meeting_agent.a2a_client:
            a2a_result = await meeting_agent.a2a_client.add_task("Direct A2A test task")
            
            if a2a_result.get("success"):
                print("✅ Direct A2A task addition successful")
                
                # Verify task was added
                task_result = task_agent.list_tasks()
                if task_result.get("success"):
                    tasks = task_result.get("data", {}).get("tasks", [])
                    print(f"📋 Total tasks after A2A addition: {len(tasks)}")
                    return True
                else:
                    print("❌ Could not verify task addition")
                    return False
            else:
                print(f"❌ Direct A2A task addition failed: {a2a_result.get('message')}")
                return False
            
    except Exception as e:
        print(f"❌ Direct A2A communication test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_action_item_extraction():
    """Test action item extraction without delegation."""
    print("\n🔍 Testing Action Item Extraction")
    print("=" * 60)
    
    try:
        from agents.meeting_assistant_agent import MeetingAssistantAgent
        
        meeting_agent = MeetingAssistantAgent()
        
        # Test text with various action item keywords
        test_text = """
        Meeting notes:
        - Action: Send email to client
        - Follow up: Call supplier about delivery
        - TODO: Update documentation
        - Task: Review code changes
        - Deadline: Submit report by EOD
        - ACTION: Schedule team meeting
        - Follow-up: Prepare presentation
        """
        
        print("📝 Extracting action items from test text...")
        action_items = meeting_agent.extract_action_items(test_text)
        
        if action_items:
            print(f"✅ Extracted {len(action_items)} action items:")
            for i, item in enumerate(action_items, 1):
                print(f"  {i}. {item}")
            return True
        else:
            print("❌ No action items extracted")
            return False
            
    except Exception as e:
        print(f"❌ Action item extraction test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_task_completion_via_a2a():
    """Test task completion via A2A communication."""
    print("\n✅ Testing Task Completion via A2A")
    print("=" * 60)
    
    try:
        from agents.meeting_assistant_agent import MeetingAssistantAgent
        from agents.task_manager_agent import TaskManagerAgent
        
        # Initialize agents
        meeting_agent = MeetingAssistantAgent()
        task_agent = TaskManagerAgent()
        
        # Use the Meeting Assistant's A2A client with proper async context manager
        async with meeting_agent.a2a_client:
            # First, add a task via A2A
            print("📤 Adding test task via A2A...")
            a2a_result = await meeting_agent.a2a_client.add_task("Task to complete via A2A")
            
            if not a2a_result.get("success"):
                print("❌ Failed to add task for completion test")
                return False
            
            task_id = a2a_result.get("data", {}).get("task_id")
            print(f"✅ Task added with ID: {task_id}")
            
            # Now complete the task via A2A
            print(f"✅ Completing task {task_id} via A2A...")
            complete_result = await meeting_agent.a2a_client.mark_task_complete(str(task_id))
            
            if complete_result.get("success"):
                print("✅ Task completion via A2A successful")
                
                # Verify task is marked as complete
                task_result = task_agent.list_tasks()
                if task_result.get("success"):
                    tasks = task_result.get("data", {}).get("tasks", [])
                    for task in tasks:
                        if str(task.get("id")) == str(task_id):
                            if task.get("status") == "completed":
                                print("✅ Task status correctly updated to completed")
                                return True
                            else:
                                print(f"❌ Task status not updated: {task.get('status')}")
                                return False
                    print("❌ Could not find task to verify completion")
                    return False
                else:
                    print("❌ Could not verify task completion")
                    return False
            else:
                print(f"❌ Task completion via A2A failed: {complete_result.get('message')}")
                return False
            
    except Exception as e:
        print(f"❌ Task completion test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_task_delegation():
    """Test simple task delegation without problematic task count verification."""
    print("\n🤖 Testing Simple Task Delegation")
    print("=" * 60)
    
    try:
        from agents.meeting_assistant_agent import MeetingAssistantAgent
        from agents.task_manager_agent import TaskManagerAgent
        
        # Initialize agents
        meeting_agent = MeetingAssistantAgent()
        task_agent = TaskManagerAgent()
        
        # Get initial tasks
        initial_tasks_result = task_agent.list_tasks()
        if initial_tasks_result.get("success"):
            initial_tasks = initial_tasks_result.get("data", {}).get("tasks", [])
            initial_count = len(initial_tasks)
        else:
            print(f"⚠️ Could not get initial tasks: {initial_tasks_result.get('message')}")
            initial_count = 0
        print(f"📊 Initial tasks: {initial_count}")
        
        # Test meeting notes with action items
        meeting_notes = """
        Quick Team Meeting:
        
        Action: Send email to client about project update
        Follow up: Schedule next meeting with team
        TODO: Update project documentation
        """
        
        print("\n📝 Processing meeting notes...")
        print(f"Meeting notes: {meeting_notes.strip()}")
        
        # Process meeting notes (this should delegate tasks via A2A)
        result = await meeting_agent.process_meeting_notes(meeting_notes)
        
        if result.get("success"):
            data = result.get("data", {})
            action_items = data.get("action_items", [])
            delegation_result = data.get("delegation_result", {})
            
            print(f"\n✅ Found {len(action_items)} action items:")
            for i, item in enumerate(action_items, 1):
                print(f"  {i}. {item}")
            
            if delegation_result:
                successful = delegation_result.get("successful_delegations", 0)
                failed = delegation_result.get("failed_delegations", 0)
                print(f"\n📤 Delegation Results:")
                print(f"  ✓ Successfully delegated: {successful} tasks")
                if failed > 0:
                    print(f"  ✗ Failed to delegate: {failed} tasks")
                
                # Wait a moment for A2A communication to complete
                time.sleep(2)
                
                # Check if tasks were actually added by listing them
                final_tasks_result = task_agent.list_tasks()
                if final_tasks_result.get("success"):
                    final_tasks = final_tasks_result.get("data", {}).get("tasks", [])
                    final_count = len(final_tasks)
                    tasks_added = final_count - initial_count
                    
                    print(f"\n📊 Task Count After Delegation:")
                    print(f"  Initial: {initial_count}")
                    print(f"  Final: {final_count}")
                    print(f"  Tasks Added: {tasks_added}")
                    
                    if tasks_added > 0:
                        print(f"✅ Task delegation successful! {tasks_added} tasks added via A2A")
                        
                        # Show the newly added tasks
                        print(f"\n📋 Current Tasks ({len(final_tasks)}):")
                        for task in final_tasks:
                            status_icon = "✓" if task.get("status") == "completed" else "○"
                            print(f"  {status_icon} {task.get('id')}. {task.get('description')}")
                        
                        return True
                    else:
                        print("❌ Task delegation failed - no tasks were added")
                        return False
                else:
                    print(f"❌ Could not get final tasks: {final_tasks_result.get('message')}")
                    return False
            else:
                print("❌ No delegation result received")
                return False
        else:
            print(f"❌ Failed to process meeting notes: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Simple task delegation test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all task delegation tests."""
    print("=" * 80)
    print("Task Delegation Test Suite - Multi-Agent Task Manager System")
    print("=" * 80)
    
    tests = [
        ("Action Item Extraction", test_action_item_extraction),
        ("Meeting Assistant → Task Manager Delegation", test_meeting_assistant_to_task_manager_delegation),
        ("Direct A2A Communication", test_direct_a2a_communication),
        ("Task Completion via A2A", test_task_completion_via_a2a),
        ("Simple Task Delegation", test_simple_task_delegation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 60)
        
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 80)
    print(f"Task Delegation Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All task delegation tests passed! A2A communication is working correctly.")
        return 0
    else:
        print("⚠️ Some task delegation tests failed. Check A2A configuration and agent setup.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 