#!/usr/bin/env python3
"""
Task Manager Agent for ADK with Ollama Support
Based on official ADK Ollama examples
"""

import asyncio
import logging
from typing import AsyncIterator
import httpx

from google.adk.agents import LlmAgent
from google.adk.models import BaseLlm, LlmResponse
import litellm
from google.genai.types import Content, Part

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_SERVER_URL = "http://localhost:8002"

def add_task_tool(description: str) -> str:
    resp = httpx.post(f"{MCP_SERVER_URL}/tools/add_task", json={"description": description})
    return resp.json().get("message", "No response from MCP server.")

def list_tasks_tool() -> str:
    resp = httpx.get(f"{MCP_SERVER_URL}/tools/list_tasks")
    data = resp.json()
    if data.get("success"):
        tasks = data.get("tasks", [])
        if not tasks:
            return "No tasks found."
        return "\n".join([f"{t['id']}: {t['description']} ({t['status']})" for t in tasks])
    return data.get("message", "No response from MCP server.")

def mark_task_complete_tool(task_id: str) -> str:
    resp = httpx.post(f"{MCP_SERVER_URL}/tools/mark_task_complete", json={"task_id": task_id})
    return resp.json().get("message", "No response from MCP server.")

def delete_task_tool(task_id: str) -> str:
    resp = httpx.post(f"{MCP_SERVER_URL}/tools/delete_task", json={"task_id": task_id})
    return resp.json().get("message", "No response from MCP server.")

def clear_all_tasks_tool() -> str:
    resp = httpx.post(f"{MCP_SERVER_URL}/tools/clear_all_tasks")
    return resp.json().get("message", "No response from MCP server.")

class OllamaLlm(BaseLlm):
    """Custom LLM wrapper for Ollama using LiteLLM.
    
    Based on ADK documentation recommendations for Ollama integration.
    Uses the ollama provider for better compatibility.
    """
    
    model: str

    def __init__(self, model_name: str = "mistral:latest"):
        super().__init__(model=f"ollama/{model_name}")
        litellm.set_verbose = False
        
    async def generate_content_async(self, prompt: str, **kwargs):
        """Generate text using Ollama via LiteLLM as an async generator."""
        try:
            # Handle case where prompt might be an LlmRequest object
            if hasattr(prompt, 'content'):
                prompt_content = prompt.content
            elif isinstance(prompt, dict) and 'content' in prompt:
                prompt_content = prompt['content']
            else:
                prompt_content = str(prompt)
            
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt_content}],
                api_base="http://localhost:11434",
                api_key="ollama",  # Required for Ollama
                **kwargs
            )
            
            # Create proper ADK Content object with Part containing text
            content = Content(
                parts=[Part(text=response.choices[0].message.content)],
                role="model"
            )
            
            # Create proper ADK LlmResponse with usage_metadata
            from google.genai.types import GenerateContentResponseUsageMetadata
            
            # Extract usage metadata from LiteLLM response if available
            usage_metadata = None
            if hasattr(response, 'usage') and response.usage:
                usage_metadata = GenerateContentResponseUsageMetadata(
                    prompt_token_count=response.usage.get('prompt_tokens', 0),
                    candidates_token_count=response.usage.get('completion_tokens', 0),
                    total_token_count=response.usage.get('total_tokens', 0)
                )
            
            llm_response = LlmResponse(
                content=content,
                usage_metadata=usage_metadata
            )
            
            yield llm_response
            
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {e}")
            # Create error response with proper ADK LlmResponse structure
            error_content = Content(
                parts=[Part(text=f"Error: {e}")],
                role="model"
            )
            
            error_response = LlmResponse(
                content=error_content,
                error_code="GENERATION_ERROR",
                error_message=str(e)
            )
            
            yield error_response

# Create the agent with custom Ollama LLM
root_agent = LlmAgent(
    model=OllamaLlm("mistral:latest"),
    name="task_manager_agent",
    description="A task management agent that can help with basic task operations using Ollama.",
    instruction="""You are a task management assistant. You MUST call the appropriate tool function for every user request.

AVAILABLE TOOLS:
- list_tasks_tool() - Returns the current list of tasks
- add_task_tool(description) - Adds a new task
- mark_task_complete_tool(task_id) - Marks a task as complete
- delete_task_tool(task_id) - Deletes a task
- clear_all_tasks_tool() - Deletes all tasks

CRITICAL INSTRUCTIONS:
1. You MUST call the actual tool functions. Do NOT describe what you would do.
2. Do NOT write code examples or describe actions.
3. Do NOT say "I will call" or "I would call" - just CALL the tools directly.
4. When asked to list tasks, call list_tasks_tool() and show the result.
5. When asked to add a task, call add_task_tool(description) with the task description.
6. When asked to mark a task complete, call mark_task_complete_tool(task_id).
7. When asked to delete a task, call delete_task_tool(task_id).

EXAMPLES OF CORRECT BEHAVIOR:
- User: "show my tasks" → Call list_tasks_tool() and display the result
- User: "list tasks" → Call list_tasks_tool() and display the result
- User: "what tasks do I have" → Call list_tasks_tool() and display the result
- User: "add task buy groceries" → Call add_task_tool("buy groceries")
- User: "mark task 1 complete" → Call mark_task_complete_tool("1")

NEVER describe what you would do. ALWAYS call the actual tool function and show the real results.
DO NOT write code examples or describe actions - just execute the tools directly.""",
    tools=[add_task_tool, list_tasks_tool, mark_task_complete_tool, delete_task_tool, clear_all_tasks_tool]
)

if __name__ == "__main__":
    print("Task Manager Agent ready!")
    print("Available commands:")
    print("- add task [description]")
    print("- list tasks") 
    print("- mark task [ID] complete")
    print("- delete task [ID]") 