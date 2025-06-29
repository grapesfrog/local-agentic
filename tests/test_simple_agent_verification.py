#!/usr/bin/env python3
"""
Simple verification test for agents with Mistral model.
This test verifies the core functionality without requiring interactive CLI.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

# Test configuration
MCP_SERVER_URL = "http://localhost:8002"
TEST_TASK_DESCRIPTION = "Simple verification test task"

class SimpleAgentVerifier:
    """Simple verification for agent functionality with Mistral."""
    
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
    
    async def test_mcp_server_functionality(self) -> bool:
        """Test MCP server core functionality."""
        try:
            # Test health
            async with self.session.get(f"{MCP_SERVER_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "healthy":
                        self.log_test("MCP Server Health", True, "Server is healthy")
                    else:
                        self.log_test("MCP Server Health", False, f"Server status: {data.get('status')}")
                        return False
                else:
                    self.log_test("MCP Server Health", False, f"HTTP {response.status}")
                    return False
            
            # Test task creation
            async with self.session.post(
                f"{MCP_SERVER_URL}/tools/add_task",
                json={"description": TEST_TASK_DESCRIPTION}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        task_id = data.get("task", {}).get("id")
                        self.log_test("MCP Task Creation", True, f"Task created with ID: {task_id}")
                    else:
                        self.log_test("MCP Task Creation", False, f"Failed: {data.get('error')}")
                        return False
                else:
                    self.log_test("MCP Task Creation", False, f"HTTP {response.status}")
                    return False
            
            # Test task listing
            async with self.session.get(f"{MCP_SERVER_URL}/tools/list_tasks") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        tasks = data.get("tasks", [])
                        test_task = next((t for t in tasks if TEST_TASK_DESCRIPTION in t.get("description", "")), None)
                        if test_task:
                            self.log_test("MCP Task Listing", True, f"Found {len(tasks)} tasks, including test task")
                            return True
                        else:
                            self.log_test("MCP Task Listing", False, "Test task not found in list")
                            return False
                    else:
                        self.log_test("MCP Task Listing", False, f"Failed: {data.get('error')}")
                        return False
                else:
                    self.log_test("MCP Task Listing", False, f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("MCP Server Functionality", False, f"Error: {e}")
            return False
    
    async def test_mistral_model_availability(self) -> bool:
        """Test that Mistral model is available in Ollama."""
        try:
            async with self.session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    if "mistral:latest" in models:
                        self.log_test("Mistral Model Availability", True, "Mistral model available in Ollama")
                        return True
                    else:
                        self.log_test("Mistral Model Availability", False, f"Available models: {models}")
                        return False
                else:
                    self.log_test("Mistral Model Availability", False, "Cannot check Ollama models")
                    return False
        except Exception as e:
            self.log_test("Mistral Model Availability", False, f"Error checking models: {e}")
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
        print("\n" + "=" * 50)
        print("SIMPLE AGENT VERIFICATION SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["passed"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All core functionality tests passed!")
            print("✅ MCP Server is working correctly")
            print("✅ Mistral model is available and configured")
            print("✅ Task management via MCP is functional")
            print("✅ ADK Web UI is accessible")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return passed == total

async def test_simple_agent_verification():
    """Main test function for simple agent verification."""
    verifier = SimpleAgentVerifier()
    
    try:
        await verifier.setup()
        
        # Run core tests
        await verifier.test_mistral_model_availability()
        await verifier.test_mcp_server_functionality()
        await verifier.test_adk_web_ui_availability()
        
        # Print summary
        all_passed = verifier.print_summary()
        
        # Assert overall success
        assert all_passed, "Some core functionality tests failed"
        
    finally:
        await verifier.teardown()

if __name__ == "__main__":
    # Run the test directly
    asyncio.run(test_simple_agent_verification()) 