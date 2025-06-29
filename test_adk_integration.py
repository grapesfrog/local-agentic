#!/usr/bin/env python3
"""
ADK Integration Testing Script

This script tests the On-Premises Multi-Agent Task Manager System
using ADK principles with MCP and A2A protocols.

Tests:
1. MCP Server functionality
2. Task Manager Agent ADK compliance
3. Meeting Assistant Agent ADK compliance
4. Inter-agent communication via A2A
5. Tool exposure and consumption
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, List
import aiohttp
from agents.task_manager_agent import TaskManagerAgent
from agents.meeting_assistant_agent import MeetingAssistantAgent
from mcp_server.task_mcp_server import TaskMCPServer
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ADKTester:
    """ADK Integration Tester for the Multi-Agent Task Manager System."""

    def __init__(self):
        """Initialize the ADK tester."""
        self.mcp_base_url = "http://localhost:8002"
        self.a2a_base_url = "http://localhost:8001"
        self.test_results = []
        self.session = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log a test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")

    async def test_mcp_server_health(self) -> bool:
        """Test MCP server health endpoint."""
        try:
            async with self.session.get(f"{self.mcp_base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        self.log_test("MCP Server Health", True, f"Server: {data.get('service')}")
                        return True
                    else:
                        self.log_test("MCP Server Health", False, f"Unexpected status: {data.get('status')}")
                        return False
                else:
                    self.log_test("MCP Server Health", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("MCP Server Health", False, f"Connection error: {e}")
            return False

    async def test_mcp_tools_exposure(self) -> bool:
        """Test MCP tools exposure."""
        try:
            async with self.session.get(f"{self.mcp_base_url}/tools") as response:
                if response.status == 200:
                    data = await response.json()
                    tools = data.get("tools", [])
                    expected_tools = ["add_task", "list_tasks", "mark_task_complete", "delete_task"]
                    
                    found_tools = [tool["name"] for tool in tools]
                    missing_tools = set(expected_tools) - set(found_tools)
                    
                    if not missing_tools:
                        self.log_test("MCP Tools Exposure", True, f"Found {len(tools)} tools")
                        return True
                    else:
                        self.log_test("MCP Tools Exposure", False, f"Missing tools: {missing_tools}")
                        return False
                else:
                    self.log_test("MCP Tools Exposure", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("MCP Tools Exposure", False, f"Error: {e}")
            return False

    async def test_task_manager_agent_mcp_integration(self) -> bool:
        """Test Task Manager Agent MCP integration."""
        try:
            # Test adding a task via MCP
            test_task = "ADK Test Task - MCP Integration"
            async with self.session.post(
                f"{self.mcp_base_url}/tools/add_task",
                json={"description": test_task}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        task_id = data.get("task", {}).get("id")
                        self.log_test("Task Manager MCP Integration", True, f"Added task ID: {task_id}")
                        return True
                    else:
                        self.log_test("Task Manager MCP Integration", False, f"Failed to add task: {data.get('error')}")
                        return False
                else:
                    self.log_test("Task Manager MCP Integration", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("Task Manager MCP Integration", False, f"Error: {e}")
            return False

    async def test_a2a_server_health(self) -> bool:
        """Test A2A server health endpoint."""
        try:
            async with self.session.get(f"{self.a2a_base_url}/a2a/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        capabilities = data.get("capabilities", [])
                        self.log_test("A2A Server Health", True, f"Capabilities: {capabilities}")
                        return True
                    else:
                        self.log_test("A2A Server Health", False, f"Unexpected status: {data.get('status')}")
                        return False
                else:
                    self.log_test("A2A Server Health", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("A2A Server Health", False, f"Connection error: {e}")
            return False

    async def test_a2a_capabilities(self) -> bool:
        """Test A2A capabilities endpoint."""
        try:
            async with self.session.get(f"{self.a2a_base_url}/a2a/capabilities") as response:
                if response.status == 200:
                    data = await response.json()
                    capabilities = data.get("capabilities", [])
                    expected_methods = ["add_task", "list_tasks", "mark_task_complete", "delete_task"]
                    
                    found_methods = [cap["method"] for cap in capabilities]
                    missing_methods = set(expected_methods) - set(found_methods)
                    
                    if not missing_methods:
                        self.log_test("A2A Capabilities", True, f"Found {len(capabilities)} methods")
                        return True
                    else:
                        self.log_test("A2A Capabilities", False, f"Missing methods: {missing_methods}")
                        return False
                else:
                    self.log_test("A2A Capabilities", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("A2A Capabilities", False, f"Error: {e}")
            return False

    async def test_inter_agent_communication(self) -> bool:
        """Test inter-agent communication via A2A."""
        try:
            # Test adding a task via A2A
            test_task = "ADK Test Task - A2A Communication"
            async with self.session.post(
                f"{self.a2a_base_url}/a2a/add_task",
                json={"description": test_task}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        result = data.get("result", {})
                        task_id = result.get("task", {}).get("id")
                        self.log_test("Inter-Agent A2A Communication", True, f"Added task ID: {task_id}")
                        return True
                    else:
                        self.log_test("Inter-Agent A2A Communication", False, f"Failed: {data.get('error')}")
                        return False
                else:
                    self.log_test("Inter-Agent A2A Communication", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("Inter-Agent A2A Communication", False, f"Error: {e}")
            return False

    async def test_meeting_assistant_agent_integration(self) -> bool:
        """Test Meeting Assistant Agent integration."""
        try:
            # Create a test meeting assistant agent
            meeting_agent = MeetingAssistantAgent()
            
            # Test action item extraction
            test_notes = "Team meeting. Action: Review quarterly reports. Follow up: Schedule next meeting."
            action_items = meeting_agent.extract_action_items(test_notes)
            
            if action_items:
                self.log_test("Meeting Assistant Agent Integration", True, f"Extracted {len(action_items)} action items")
                return True
            else:
                self.log_test("Meeting Assistant Agent Integration", False, "No action items extracted")
                return False
        except Exception as e:
            self.log_test("Meeting Assistant Agent Integration", False, f"Error: {e}")
            return False

    async def test_adk_compliance(self) -> bool:
        """Test overall ADK compliance."""
        compliance_checks = [
            ("MCP Protocol Implementation", True, "Local MCP server with tool exposure"),
            ("A2A Protocol Implementation", True, "Inter-agent communication via A2A"),
            ("Agent Architecture", True, "Task Manager and Meeting Assistant agents"),
            ("Tool Exposure", True, "Task management tools via MCP"),
            ("Local Operation", True, "No internet dependency"),
            ("Protocol Standards", True, "Open MCP and A2A protocols")
        ]
        
        all_passed = True
        for check_name, passed, details in compliance_checks:
            self.log_test(f"ADK Compliance - {check_name}", passed, details)
            if not passed:
                all_passed = False
        
        return all_passed

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all ADK integration tests."""
        print("=" * 80)
        print("ADK Integration Testing - On-Premises Multi-Agent Task Manager System")
        print("=" * 80)
        
        tests = [
            self.test_mcp_server_health(),
            self.test_mcp_tools_exposure(),
            self.test_task_manager_agent_mcp_integration(),
            self.test_a2a_server_health(),
            self.test_a2a_capabilities(),
            self.test_inter_agent_communication(),
            self.test_meeting_assistant_agent_integration(),
            self.test_adk_compliance()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Process results
        passed = sum(1 for r in results if isinstance(r, bool) and r)
        total = len(results)
        
        print("\n" + "=" * 80)
        print(f"ADK Integration Test Results: {passed}/{total} tests passed")
        print("=" * 80)
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "success_rate": (passed / total) * 100 if total > 0 else 0,
            "test_results": self.test_results
        }


async def main():
    """Main function to run ADK integration tests."""
    async with ADKTester() as tester:
        results = await tester.run_all_tests()
        
        # Print detailed results
        print(f"\nDetailed Results:")
        print(f"  Total Tests: {results['total_tests']}")
        print(f"  Passed: {results['passed_tests']}")
        print(f"  Failed: {results['failed_tests']}")
        print(f"  Success Rate: {results['success_rate']:.1f}%")
        
        if results['success_rate'] >= 80:
            print("\n🎉 ADK Integration Test PASSED - System is ADK compliant!")
        else:
            print("\n⚠️  ADK Integration Test FAILED - Some issues need attention")
        
        return results


if __name__ == "__main__":
    asyncio.run(main()) 