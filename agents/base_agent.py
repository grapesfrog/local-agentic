"""Base agent class providing common functionality for all agents."""

import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(self, name: str):
        """Initialize the base agent."""
        self.name = name
        self.setup_logging()

    def setup_logging(self) -> None:
        """Setup logging for the agent."""
        log_level = os.getenv("LOG_LEVEL", "INFO")
        debug_mode = os.getenv("DEBUG", "false").lower() == "true"
        
        if debug_mode:
            log_level = "DEBUG"
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger.info(f"Agent '{self.name}' initialized with log level: {log_level}")

    def log_info(self, message: str) -> None:
        """Log an info message."""
        logger.info(f"[{self.name}] {message}")

    def log_error(self, message: str) -> None:
        """Log an error message."""
        logger.error(f"[{self.name}] {message}")

    def log_debug(self, message: str) -> None:
        """Log a debug message."""
        logger.debug(f"[{self.name}] {message}")

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        logger.warning(f"[{self.name}] {message}")

    def validate_input(self, input_data: Any, expected_type: type, field_name: str) -> bool:
        """Validate input data."""
        if not isinstance(input_data, expected_type):
            self.log_error(f"Invalid {field_name}: expected {expected_type.__name__}, got {type(input_data).__name__}")
            return False
        return True

    def format_response(self, success: bool, message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Format a standardized response."""
        response = {
            "success": success,
            "message": message,
            "agent": self.name
        }
        
        if data:
            response["data"] = data
            
        return response

    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle and log an error."""
        error_message = f"Error in {context}: {str(error)}" if context else str(error)
        self.log_error(error_message)
        
        return self.format_response(
            success=False,
            message=error_message
        )

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value from environment."""
        return os.getenv(key, default)

    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get_config("DEBUG", "false").lower() == "true" 