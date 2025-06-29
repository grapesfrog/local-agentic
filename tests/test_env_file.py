import os
import pytest
from dotenv import load_dotenv

def test_env_file_loaded():
    load_dotenv(dotenv_path=".env", override=True)
    # Example: Check for a required variable
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY not set in .env file" 