from src.tools import (
    get_airport_metrics,
    calculate_driver_incentive,
    trigger_surge_override,
)


def test_get_airport_metrics():
    result = get_airport_metrics("SFO")

    assert result["airport_code"] == "SFO"
    assert result["surge_multiplier"] == 1.6


def test_calculate_driver_incentive():
    result = calculate_driver_incentive("SFO", 102, 185, 58)

    assert result["proposed_incentive"] == 25.0
    assert result["impact_level"] == "medium"


def test_surge_requires_approval():
    result = trigger_surge_override("SFO", 1.6)

    assert result["status"] == "approval_required"


def test_surge_rejects_above_limit():
    result = trigger_surge_override("SFO", 2.1)

    assert result["status"] == "rejected"


def test_surge_executes_after_approval():
    result = trigger_surge_override("SFO", 1.6, approved=True)

    assert result["status"] == "executed"
