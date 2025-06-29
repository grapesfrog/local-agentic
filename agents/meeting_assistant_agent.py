"""Meeting Assistant Agent implementation."""

import re
import os
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from protocols.a2a_server import A2AClient
import logging

logger = logging.getLogger(__name__)


class MeetingAssistantAgent(BaseAgent):
    """Meeting Assistant Agent that processes meeting notes and delegates tasks."""

    def __init__(self):
        """Initialize the Meeting Assistant Agent."""
        super().__init__("MeetingAssistantAgent")
        self.a2a_client = A2AClient()
        self.task_keywords = [
            "action:", "action item:", "todo:", "to do:", "follow up:", 
            "follow-up:", "task:", "need to:", "must:", "should:",
            "action items:", "todos:", "tasks:", "next steps:"
        ]

    def extract_action_items(self, meeting_notes: str) -> List[str]:
        """Extract action items from meeting notes using keyword matching."""
        try:
            if not self.validate_input(meeting_notes, str, "meeting_notes"):
                return []

            self.log_info("Extracting action items from meeting notes")
            
            # Convert to lowercase for case-insensitive matching
            notes_lower = meeting_notes.lower()
            action_items = []
            
            # Split into sentences and look for action items
            sentences = re.split(r'[.!?]+', meeting_notes)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Check if sentence contains action keywords
                for keyword in self.task_keywords:
                    if keyword in sentence.lower():
                        # Extract the action item (everything after the keyword)
                        keyword_index = sentence.lower().find(keyword)
                        action_item = sentence[keyword_index + len(keyword):].strip()
                        
                        # Clean up the action item
                        action_item = re.sub(r'^[:\s]+', '', action_item)  # Remove leading colons/spaces
                        action_item = re.sub(r'[:\s]+$', '', action_item)  # Remove trailing colons/spaces
                        
                        if action_item and len(action_item) > 3:  # Minimum length check
                            action_items.append(action_item)
                            self.log_debug(f"Found action item: {action_item}")
                        break
            
            # Also look for patterns like "Action: ..." or "TODO: ..."
            for keyword in self.task_keywords:
                pattern = rf'{re.escape(keyword)}\s*([^.!?]+)'
                matches = re.findall(pattern, notes_lower)
                for match in matches:
                    action_item = match.strip()
                    if action_item and len(action_item) > 3 and action_item not in [item.lower() for item in action_items]:
                        action_items.append(action_item)
                        self.log_debug(f"Found action item via pattern: {action_item}")
            
            # Remove duplicates while preserving order
            unique_items = []
            seen = set()
            for item in action_items:
                item_lower = item.lower()
                if item_lower not in seen:
                    unique_items.append(item)
                    seen.add(item_lower)
            
            self.log_info(f"Extracted {len(unique_items)} unique action items")
            return unique_items
            
        except Exception as e:
            self.log_error(f"Error extracting action items: {e}")
            return []

    async def delegate_tasks(self, action_items: List[str]) -> Dict[str, Any]:
        """Delegate action items as tasks to the Task Manager Agent via A2A."""
        try:
            if not self.validate_input(action_items, list, "action_items"):
                return self.format_response(False, "Invalid action items format")

            if not action_items:
                return self.format_response(True, "No action items to delegate")

            self.log_info(f"Delegating {len(action_items)} action items as tasks")
            
            delegated_tasks = []
            failed_tasks = []
            
            async with self.a2a_client:
                for action_item in action_items:
                    try:
                        self.log_debug(f"Delegating task: {action_item}")
                        result = await self.a2a_client.add_task(action_item)
                        
                        if result.get("success"):
                            task_data = result.get("result", {}).get("task", {})
                            delegated_tasks.append({
                                "description": action_item,
                                "task_id": task_data.get("id"),
                                "status": "delegated"
                            })
                            self.log_info(f"Successfully delegated task: {action_item} (ID: {task_data.get('id')})")
                        else:
                            failed_tasks.append({
                                "description": action_item,
                                "error": result.get("error", "Unknown error")
                            })
                            self.log_error(f"Failed to delegate task: {action_item} - {result.get('error')}")
                    except Exception as e:
                        failed_tasks.append({
                            "description": action_item,
                            "error": str(e)
                        })
                        self.log_error(f"Exception while delegating task: {action_item} - {e}")

            # Prepare response
            total_items = len(action_items)
            successful_delegations = len(delegated_tasks)
            failed_delegations = len(failed_tasks)
            
            message = f"Delegated {successful_delegations} out of {total_items} action items as tasks"
            if failed_delegations > 0:
                message += f" ({failed_delegations} failed)"
            
            self.log_info(message)
            
            return self.format_response(
                success=True,
                message=message,
                data={
                    "delegated_tasks": delegated_tasks,
                    "failed_tasks": failed_tasks,
                    "total_items": total_items,
                    "successful_delegations": successful_delegations,
                    "failed_delegations": failed_delegations
                }
            )
            
        except Exception as e:
            return self.handle_error(e, "delegate tasks")

    async def process_meeting_notes(self, meeting_notes: str) -> Dict[str, Any]:
        """Process meeting notes to extract and delegate action items."""
        try:
            if not self.validate_input(meeting_notes, str, "meeting_notes"):
                return self.format_response(False, "Invalid meeting notes format")

            if not meeting_notes.strip():
                return self.format_response(False, "Meeting notes cannot be empty")

            self.log_info("Processing meeting notes")
            
            # Extract action items
            action_items = self.extract_action_items(meeting_notes)
            
            if not action_items:
                return self.format_response(
                    True, 
                    "No action items found in the meeting notes",
                    {"action_items": [], "delegated_tasks": []}
                )
            
            # Delegate tasks
            delegation_result = await self.delegate_tasks(action_items)
            
            if delegation_result.get("success"):
                data = delegation_result.get("data", {})
                return self.format_response(
                    True,
                    f"Processed meeting notes: {data.get('successful_delegations', 0)} tasks delegated",
                    {
                        "action_items": action_items,
                        "delegation_result": data
                    }
                )
            else:
                return self.format_response(
                    False,
                    f"Failed to delegate tasks: {delegation_result.get('message')}",
                    {"action_items": action_items}
                )
                
        except Exception as e:
            return self.handle_error(e, "process meeting notes")

    async def process_meeting_file(self, file_path: str) -> Dict[str, Any]:
        """Process meeting notes from a file."""
        try:
            if not self.validate_input(file_path, str, "file_path"):
                return self.format_response(False, "Invalid file path")

            if not os.path.exists(file_path):
                return self.format_response(False, f"File not found: {file_path}")

            self.log_info(f"Processing meeting notes from file: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    meeting_notes = file.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as file:
                    meeting_notes = file.read()
            
            if not meeting_notes.strip():
                return self.format_response(False, "File is empty")
            
            # Process the meeting notes
            return await self.process_meeting_notes(meeting_notes)
            
        except Exception as e:
            return self.handle_error(e, "process meeting file")

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the A2A connection."""
        try:
            self.log_info("Checking A2A connection health")
            
            async with self.a2a_client:
                result = await self.a2a_client.health_check()
                
                if result.get("status") == "healthy":
                    message = "A2A connection is healthy"
                    self.log_info(message)
                    return self.format_response(True, message, result)
                else:
                    error_msg = "A2A connection is not healthy"
                    self.log_error(error_msg)
                    return self.format_response(False, error_msg, result)
                    
        except Exception as e:
            return self.handle_error(e, "A2A health check")

    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the Meeting Assistant Agent."""
        capabilities = {
            "agent_name": self.name,
            "capabilities": [
                "process_meeting_notes",
                "process_meeting_file",
                "extract_action_items",
                "delegate_tasks",
                "health_check"
            ],
            "supported_keywords": self.task_keywords,
            "supported_file_formats": ["txt", "md"]
        }
        
        return self.format_response(True, "Capabilities retrieved", capabilities)

    def add_custom_keyword(self, keyword: str) -> Dict[str, Any]:
        """Add a custom keyword for action item detection."""
        try:
            if not self.validate_input(keyword, str, "keyword"):
                return self.format_response(False, "Invalid keyword format")

            keyword_lower = keyword.lower()
            if keyword_lower not in self.task_keywords:
                self.task_keywords.append(keyword_lower)
                self.log_info(f"Added custom keyword: {keyword}")
                return self.format_response(True, f"Added custom keyword: {keyword}")
            else:
                return self.format_response(False, f"Keyword '{keyword}' already exists")

        except Exception as e:
            return self.handle_error(e, "add custom keyword")

    def remove_custom_keyword(self, keyword: str) -> Dict[str, Any]:
        """Remove a custom keyword from action item detection."""
        try:
            if not self.validate_input(keyword, str, "keyword"):
                return self.format_response(False, "Invalid keyword format")

            keyword_lower = keyword.lower()
            if keyword_lower in self.task_keywords:
                self.task_keywords.remove(keyword_lower)
                self.log_info(f"Removed custom keyword: {keyword}")
                return self.format_response(True, f"Removed custom keyword: {keyword}")
            else:
                return self.format_response(False, f"Keyword '{keyword}' not found")

        except Exception as e:
            return self.handle_error(e, "remove custom keyword") 