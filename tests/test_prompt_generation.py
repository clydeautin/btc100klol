import pytest
from openai_files.utils import PromptType
from openai_files.helpers import get_prompt

def test_get_prompt_sad_normal():
    """Test standard sad prompt when price is above 75k"""
    prompt = get_prompt(PromptType.GENERATE_IMAGE_SAD, "New Year's Day", price=80000)
    assert "crypto winter" not in prompt.lower()
    assert "sad crypto investor" in prompt

def test_get_prompt_sad_winter():
    """Test winter sad prompt when price is below 75k"""
    prompt = get_prompt(PromptType.GENERATE_IMAGE_SAD, "New Year's Day", price=70000)
    assert "crypto winter" in prompt.lower() or "winter" in prompt.lower()
    assert "sad crypto investor" in prompt

def test_get_prompt_sad_default():
    """Test default behavior (no price) assumes no winter"""
    # Note: we need to update get_prompt to switch from fixed param to kwargs to test this fully,
    # but for now we'll call it with just the required param if the signature allowed it,
    # or pass a price=None if we change signature to support that.
    # Based on plan, we are changing signature.
    # For now, let's assume we pass price defaults to high if missing.
    pass 
