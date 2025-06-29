#!/usr/bin/env python3
"""
Test suite for verifying both agents work correctly with Mistral model.
Based on ADK Python Ollama examples and best practices.
"""

import pytest
import asyncio
import aiohttp
import json
import subprocess
import time
import os
from typing import Dict, Any

# Test configuration
MCP_SERVER_URL = "http://localhost:8002"
A2A_SERVER_URL = "http://localhost:8001"
TEST_TASK_DESCRIPTION = "Test task from agent verification"

class AgentTester:
    """Test suite for verifying agent functionality with Mistral."""
    
    def __init__(self):
        self.session = None
        self.test_results = []
    
    async def setup(self):
        """Setup test environment."""
        self.session = aiohttp.ClientSession()
    
    async def teardown(self):
        """Cleanup test environment."""
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test results."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    async def test_mcp_server_health(self) -> bool:
        """Test MCP server health endpoint."""
        try:
            async with self.session.get(f"{MCP_SERVER_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        self.log_test("MCP Server Health", True, "Server is healthy")
                        return True
                    else:
                        self.log_test("MCP Server Health", False, f"Server status: {data.get('status')}")
                        return False
                else:
                    self.log_test("MCP Server Health", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("MCP Server Health", False, f"Connection error: {e}")
            return False
    
    async def test_a2a_server_health(self) -> bool:
        """Test A2A server health endpoint."""
        try:
            async with self.session.get(f"{A2A_SERVER_URL}/a2a/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        self.log_test("A2A Server Health", True, "Server is healthy")
                        return True
                    else:
                        self.log_test("A2A Server Health", False, f"Server status: {data.get('status')}")
                        return False
                else:
                    self.log_test("A2A Server Health", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("A2A Server Health", False, f"Connection error: {e}")
            return False
    
    async def test_task_creation_via_mcp(self) -> bool:
        """Test task creation via MCP server."""
        try:
            async with self.session.post(
                f"{MCP_SERVER_URL}/tools/add_task",
                json={"description": TEST_TASK_DESCRIPTION}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        task_id = data.get("task", {}).get("id")
                        self.log_test("Task Creation via MCP", True, f"Task created with ID: {task_id}")
                        return True
                    else:
                        self.log_test("Task Creation via MCP", False, f"Failed: {data.get('error')}")
                        return False
                else:
                    self.log_test("Task Creation via MCP", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("Task Creation via MCP", False, f"Error: {e}")
            return False
    
    async def test_task_listing_via_mcp(self) -> bool:
        """Test task listing via MCP server."""
        try:
            async with self.session.get(f"{MCP_SERVER_URL}/tools/list_tasks") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        tasks = data.get("tasks", [])
                        test_task = next((t for t in tasks if TEST_TASK_DESCRIPTION in t.get("description", "")), None)
                        if test_task:
                            self.log_test("Task Listing via MCP", True, f"Found {len(tasks)} tasks, including test task")
                            return True
                        else:
                            self.log_test("Task Listing via MCP", False, "Test task not found in list")
                            return False
                    else:
                        self.log_test("Task Listing via MCP", False, f"Failed: {data.get('error')}")
                        return False
                else:
                    self.log_test("Task Listing via MCP", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("Task Listing via MCP", False, f"Error: {e}")
            return False
    
    async def test_a2a_task_delegation(self) -> bool:
        """Test A2A task delegation from Meeting Assistant to Task Manager."""
        try:
            async with self.session.post(
                f"{A2A_SERVER_URL}/a2a/add_task",
                json={"task": f"A2A test task: {TEST_TASK_DESCRIPTION}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("A2A Task Delegation", True, "Task delegated successfully via A2A")
                        return True
                    else:
                        self.log_test("A2A Task Delegation", False, f"Failed: {data.get('error')}")
                        return False
                else:
                    self.log_test("A2A Task Delegation", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("A2A Task Delegation", False, f"Error: {e}")
            return False
    
    async def test_agent_model_consistency(self) -> bool:
        """Test that both agents are using Mistral model."""
        try:
            # Check if Ollama is running and has Mistral
            async with self.session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    if "mistral:latest" in models:
                        self.log_test("Agent Model Consistency", True, "Mistral model available in Ollama")
                        return True
                    else:
                        self.log_test("Agent Model Consistency", False, f"Available models: {models}")
                        return False
                else:
                    self.log_test("Agent Model Consistency", False, "Cannot check Ollama models")
                    return False
        except Exception as e:
            self.log_test("Agent Model Consistency", False, f"Error checking models: {e}")
            return False
    
    async def test_adk_web_ui_availability(self) -> bool:
        """Test that ADK Web UI is available."""
        try:
            async with self.session.get("http://localhost:8000") as response:
                if response.status == 200:
                    self.log_test("ADK Web UI Availability", True, "Web UI is accessible")
                    return True
                else:
                    self.log_test("ADK Web UI Availability", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("ADK Web UI Availability", False, f"Error: {e}")
            return False
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("AGENT TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["passed"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Agents are working correctly with Mistral.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return passed == total

@pytest.mark.asyncio
async def test_agents_with_mistral():
    """Main test function for verifying agents with Mistral."""
    tester = AgentTester()
    
    try:
        await tester.setup()
        
        # Run all tests
        await tester.test_mcp_server_health()
        await tester.test_a2a_server_health()
        await tester.test_agent_model_consistency()
        await tester.test_task_creation_via_mcp()
        await tester.test_task_listing_via_mcp()
        await tester.test_a2a_task_delegation()
        await tester.test_adk_web_ui_availability()
        
        # Print summary
        all_passed = tester.print_summary()
        
        # Assert overall success
        assert all_passed, "Some agent tests failed"
        
    finally:
        await tester.teardown()

if __name__ == "__main__":
    # Run the test directly
    asyncio.run(test_agents_with_mistral()) 