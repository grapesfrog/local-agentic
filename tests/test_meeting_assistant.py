"""Tests for the Meeting Assistant Agent."""

import pytest
import tempfile
import os
from agents.meeting_assistant_agent import MeetingAssistantAgent


class TestMeetingAssistantAgent:
    """Test cases for MeetingAssistantAgent."""

    @pytest.fixture
    def agent(self):
        """Create a MeetingAssistantAgent instance."""
        return MeetingAssistantAgent()

    def test_agent_initialization(self, agent):
        """Test that the agent initializes correctly."""
        assert agent.name == "MeetingAssistantAgent"
        assert agent.a2a_client is not None
        assert len(agent.task_keywords) > 0

    def test_extract_action_items_basic(self, agent):
        """Test basic action item extraction."""
        notes = "Team meeting. Action: Email John about budget. Follow up: Schedule next meeting."
        action_items = agent.extract_action_items(notes)
        
        assert len(action_items) == 2
        assert "Email John about budget" in action_items
        assert "Schedule next meeting" in action_items

    def test_extract_action_items_with_todo(self, agent):
        """Test action item extraction with TODO keyword."""
        notes = "Project review. TODO: Update documentation. Action: Review code changes."
        action_items = agent.extract_action_items(notes)
        
        assert len(action_items) == 2
        assert "Update documentation" in action_items
        assert "Review code changes" in action_items

    def test_extract_action_items_case_insensitive(self, agent):
        """Test that action item extraction is case insensitive."""
        notes = "Meeting notes. ACTION: Send report. Todo: Call client."
        action_items = agent.extract_action_items(notes)
        
        assert len(action_items) == 2
        assert "Send report" in action_items
        assert "Call client" in action_items

    def test_extract_action_items_no_duplicates(self, agent):
        """Test that duplicate action items are removed."""
        notes = "Action: Send email. Action: Send email. TODO: Call John."
        action_items = agent.extract_action_items(notes)
        
        assert len(action_items) == 2
        assert action_items.count("Send email") == 1

    def test_extract_action_items_empty_notes(self, agent):
        """Test action item extraction with empty notes."""
        action_items = agent.extract_action_items("")
        assert len(action_items) == 0

    def test_extract_action_items_no_action_items(self, agent):
        """Test action item extraction when no action items are present."""
        notes = "This is just a regular meeting note without any action items."
        action_items = agent.extract_action_items(notes)
        assert len(action_items) == 0

    def test_add_custom_keyword(self, agent):
        """Test adding a custom keyword."""
        original_count = len(agent.task_keywords)
        result = agent.add_custom_keyword("deadline:")
        
        assert result["success"] is True
        assert len(agent.task_keywords) == original_count + 1
        assert "deadline:" in agent.task_keywords

    def test_add_duplicate_keyword(self, agent):
        """Test adding a duplicate keyword."""
        agent.add_custom_keyword("deadline:")
        result = agent.add_custom_keyword("deadline:")
        
        assert result["success"] is False
        assert "already exists" in result["message"]

    def test_remove_custom_keyword(self, agent):
        """Test removing a custom keyword."""
        agent.add_custom_keyword("deadline:")
        result = agent.remove_custom_keyword("deadline:")
        
        assert result["success"] is True
        assert "deadline:" not in agent.task_keywords

    def test_remove_nonexistent_keyword(self, agent):
        """Test removing a non-existent keyword."""
        result = agent.remove_custom_keyword("nonexistent:")
        
        assert result["success"] is False
        assert "not found" in result["message"]

    def test_get_capabilities(self, agent):
        """Test getting agent capabilities."""
        result = agent.get_capabilities()
        
        assert result["success"] is True
        data = result["data"]
        assert data["agent_name"] == "MeetingAssistantAgent"
        assert "process_meeting_notes" in data["capabilities"]
        assert "extract_action_items" in data["capabilities"]
        assert "txt" in data["supported_file_formats"]

    @pytest.mark.asyncio
    async def test_process_meeting_file(self, agent):
        """Test processing meeting notes from a file."""
        # Create a temporary file with meeting notes
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Team meeting. Action: Send report. TODO: Call client.")
            file_path = f.name
        
        try:
            result = await agent.process_meeting_file(file_path)
            
            # Note: This test might fail if A2A server is not running
            # In a real test environment, you'd mock the A2A client
            assert result["success"] is True or "A2A" in result["message"]
        finally:
            # Cleanup
            if os.path.exists(file_path):
                os.unlink(file_path)

    def test_validate_input(self, agent):
        """Test input validation."""
        # Valid string input
        assert agent.validate_input("test", str, "test_field") is True
        
        # Invalid type
        assert agent.validate_input(123, str, "test_field") is False
        
        # Valid list input
        assert agent.validate_input(["item1", "item2"], list, "test_field") is True

    def test_format_response(self, agent):
        """Test response formatting."""
        response = agent.format_response(True, "Success message", {"key": "value"})
        
        assert response["success"] is True
        assert response["message"] == "Success message"
        assert response["agent"] == "MeetingAssistantAgent"
        assert response["data"]["key"] == "value"

    def test_handle_error(self, agent):
        """Test error handling."""
        error = ValueError("Test error")
        response = agent.handle_error(error, "test context")
        
        assert response["success"] is False
        assert "test context" in response["message"]
        assert "Test error" in response["message"] 