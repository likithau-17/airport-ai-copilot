import pytest

from src.memory import ConversationMemory


def test_memory_stores_airport_context():
    memory = ConversationMemory()
    memory.update("What is happening at SFO?", "SFO")

    assert memory.resolve_airport() == "SFO"


def test_memory_resolves_follow_up_airport():
    memory = ConversationMemory()
    memory.update("Check SFO operations", "SFO")
    memory.update("What about it now?")

    assert memory.resolve_airport() == "SFO"


def test_memory_explicit_airport_overrides_context():
    memory = ConversationMemory()
    memory.update("Check SFO", "SFO")

    assert memory.resolve_airport("LAX") == "LAX"


def test_memory_requires_airport_context():
    memory = ConversationMemory()

    with pytest.raises(ValueError):
        memory.resolve_airport()


def test_memory_history():
    memory = ConversationMemory()
    memory.update("Check SFO", "SFO")
    memory.update("What about it now?")

    history = memory.get_history()

    assert len(history) == 2
    assert history[0]["airport_code"] == "SFO"
    assert history[1]["airport_code"] == "SFO"
