#!/usr/bin/env python3
"""
Meeting Assistant Agent for ADK
Uses Ollama with Gemma3:4b via LiteLLM and connects to A2A server for task delegation
"""

import asyncio
import aiohttp
import json
import logging
import re
from typing import Dict, Any, List
from google.adk.agents import LlmAgent
from google.adk.models import BaseLlm, LlmResponse
import litellm
from google.genai.types import Content, Part

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaLlm(BaseLlm):
    """Custom LLM wrapper for Ollama using LiteLLM.
    
    Based on ADK documentation recommendations for Ollama integration.
    Uses the ollama_chat provider for better compatibility.
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

class MeetingAssistantTools:
    """Tools for interacting with the A2A server."""
    def __init__(self):
        self.a2a_server_url = "http://localhost:8001"
        self.action_keywords = [
            "action:", "todo:", "task:", "follow up:", "next steps:",
            "deadline:", "due:", "assign:", "delegate:"
        ]
    async def setup(self):
        logger.info("Setting up Meeting Assistant Tools with A2A server")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.a2a_server_url}/a2a/health") as response:
                    if response.status == 200:
                        logger.info("✅ A2A server connection successful")
                    else:
                        logger.warning("⚠️ A2A server health check failed")
        except Exception as e:
            logger.error(f"❌ Failed to connect to A2A server: {e}")
    def extract_action_items(self, text: str) -> List[str]:
        try:
            action_items = []
            lines = text.split('\n')
            for line in lines:
                line_lower = line.lower().strip()
                # Check if line contains any action keywords
                has_action_keyword = any(keyword in line_lower for keyword in self.action_keywords)
                
                if has_action_keyword:
                    # Split the line by common separators to find multiple action items
                    parts = re.split(r'[,;]', line)
                    for part in parts:
                        part = part.strip()
                        if not part:
                            continue
                            
                        part_lower = part.lower()
                        # Check if this part contains an action keyword
                        for keyword in self.action_keywords:
                            if keyword in part_lower:
                                # Extract the action item by removing the keyword
                                action_item = re.sub(rf'{keyword}', '', part, flags=re.IGNORECASE)
                                action_item = action_item.strip()
                                if action_item:
                                    action_items.append(action_item)
                                break
            return action_items
        except Exception as e:
            logger.error(f"Error extracting action items: {e}")
            return []
    async def delegate_task(self, task_description: str) -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.a2a_server_url}/a2a/add_task",
                    json={"description": task_description}
                ) as response:
                    result = await response.json()
                    logger.info(f"Task delegated: {result}")
                    return result
        except Exception as e:
            logger.error(f"Failed to delegate task: {e}")
            return {"success": False, "error": str(e)}
    async def process_meeting_notes(self, notes_text: str) -> str:
        try:
            logger.info("Processing meeting notes...")
            action_items = self.extract_action_items(notes_text)
            if not action_items:
                return "No action items found in the meeting notes."
            delegated_tasks = []
            for item in action_items:
                result = await self.delegate_task(item)
                if result.get("success"):
                    delegated_tasks.append(f"✅ {item}")
                else:
                    delegated_tasks.append(f"❌ {item} (failed: {result.get('error', 'Unknown error')})")
            return f"Processed {len(action_items)} action items:\n" + "\n".join(delegated_tasks)
        except Exception as e:
            logger.error(f"Error processing meeting notes: {e}")
            return f"Error processing meeting notes: {e}"

# Create tools instance
tools = MeetingAssistantTools()

# Define tool functions for ADK agent
def process_meeting_notes_tool(notes_text: str) -> str:
    """Process meeting notes and delegate action items."""
    return asyncio.run(tools.process_meeting_notes(notes_text))

def extract_action_items_tool(text: str) -> str:
    """Extract action items from text without delegating."""
    action_items = tools.extract_action_items(text)
    if not action_items:
        return "No action items found in the text."
    
    return f"Found {len(action_items)} action items:\n" + "\n".join([f"- {item}" for item in action_items])

def delegate_task_tool(task_description: str) -> str:
    """Delegate a specific task to the Task Manager."""
    result = asyncio.run(tools.delegate_task(task_description))
    if result.get("success"):
        return f"✅ Task delegated successfully: {result.get('message', '')}"
    else:
        return f"❌ Failed to delegate task: {result.get('error', 'Unknown error')}"

# Create the ADK LlmAgent with Ollama and tools
agent = LlmAgent(
    model=OllamaLlm("mistral:latest"),
    name="meeting_assistant_agent",
    instruction="""You are a Meeting Assistant Agent that processes meeting notes and delegates tasks. You have access to the following tools:

1. process_meeting_notes_tool - Use this when the user provides meeting notes that need to be processed. This tool will extract action items and delegate them automatically.
2. extract_action_items_tool - Use this when the user wants to extract action items from text without delegating them.
3. delegate_task_tool - Use this when the user wants to delegate a specific task.

IMPORTANT: When the user provides meeting notes or asks you to process meeting notes, you MUST call the process_meeting_notes_tool function with the meeting notes text. Do not just describe what you can do - actually call the tool and show the results.

When you see meeting notes with action items containing keywords like:
- "action:", "todo:", "task:", "follow up:", "next steps:"
- "deadline:", "due:", "assign:", "delegate:"

You should call process_meeting_notes_tool to extract and delegate these action items.

Always call the appropriate tool function when the user makes a request, and then provide the results from the tool call.""",
    tools=[process_meeting_notes_tool, extract_action_items_tool, delegate_task_tool]
)

# Expose the agent as root_agent for ADK compatibility
root_agent = agent

if __name__ == "__main__":
    asyncio.run(tools.setup())
    print("Meeting Assistant Agent ready!")
    print("Available commands:")
    print("- process notes [meeting notes text]")
    print("- extract [text]")
    print("- delegate [task description]") 