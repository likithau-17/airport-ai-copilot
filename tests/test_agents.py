from src.agents import (
    check_policy_compliance,
    investigate_operations,
    orchestrate_operations,
    resolve_operations,
    run_conversation_turn,
)
from src.memory import ConversationMemory


def test_investigate_operations():
    result = investigate_operations("SFO")

    assert result["airport_code"] == "SFO"
    assert result["assessment"] == "Operational degradation detected."
    assert len(result["issues"]) == 4


def test_policy_compliance():
    result = check_policy_compliance("SFO", "surge", 1.6)

    assert result["status"] == "approval_required"
    assert result["approval_required"] is True


def test_resolve_operations():
    investigation = investigate_operations("SFO")
    result = resolve_operations(investigation)

    assert result["airport_code"] == "SFO"
    assert result["issues_identified"] == 4
    assert result["requires_human_review"] is True


def test_orchestrate_operations():
    result = orchestrate_operations("SFO")

    assert result["airport_code"] == "SFO"
    assert result["policy_review"]["status"] == "approval_required"


def test_conversation_memory_integration():
    memory = ConversationMemory()

    first = run_conversation_turn(
        memory,
        "What is happening at SFO?",
        "SFO",
    )
    second = run_conversation_turn(
        memory,
        "What about it now?",
    )

    assert first["resolved_airport"] == "SFO"
    assert second["resolved_airport"] == "SFO"
    assert len(memory.get_history()) == 2
