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


def test_controlled_agent_loop():
    from src.agents import run_controlled_agent_loop

    result = run_controlled_agent_loop("SFO")

    assert result["iterations"] == 3
    assert result["max_iterations"] == 5
    assert [step["agent"] for step in result["steps"]] == [
        "Operations Investigator",
        "Policy & Compliance",
        "Resolution",
    ]
    assert result["policy_review"]["status"] == "approval_required"


def test_controlled_agent_loop_never_exceeds_five_iterations():
    from src.agents import run_controlled_agent_loop

    result = run_controlled_agent_loop("SFO", max_iterations=10)

    assert result["max_iterations"] == 5
    assert result["iterations"] <= 5


def test_retrieve_policy_for_agent():
    from src.agents import retrieve_policy_for_agent

    result = retrieve_policy_for_agent(
        "What is the maximum allowed surge multiplier at SFO?"
    )

    assert result["source_count"] > 0
    assert "SFO" in result["context"]
    assert "2.0x" in result["context"]


def test_tool_registry_contains_expected_tools():
    from src.tools import TOOL_REGISTRY

    assert {
        "get_airport_metrics",
        "calculate_driver_incentive",
        "trigger_surge_override",
    }.issubset(TOOL_REGISTRY)


def test_execute_tool_call_dispatches_safely():
    from src.tools import execute_tool_call

    result = execute_tool_call(
        "get_airport_metrics",
        {"airport_code": "SFO"},
    )

    assert result["airport_code"] == "SFO"
    assert "completion_rate" in result


def test_execute_tool_call_rejects_unknown_tool():
    import pytest
    from src.tools import execute_tool_call

    with pytest.raises(ValueError, match="Unknown tool"):
        execute_tool_call("unknown_tool", {})
