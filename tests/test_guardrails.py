import pytest

from src.guardrails import classify_action_risk, validate_policy_action, process_human_approval


def test_metrics_are_low_risk():
    result = classify_action_risk("metrics")

    assert result["risk_level"] == "low"
    assert result["approval_required"] is False
    assert result["status"] == "allowed"


def test_policy_lookup_is_low_risk():
    result = classify_action_risk("policy_lookup")

    assert result["risk_level"] == "low"
    assert result["approval_required"] is False


def test_incentive_up_to_25_is_medium():
    result = classify_action_risk("incentive", 25)

    assert result["risk_level"] == "medium"
    assert result["approval_required"] is False
    assert result["status"] == "allowed"


def test_incentive_above_25_requires_approval():
    result = classify_action_risk("incentive", 30)

    assert result["risk_level"] == "high"
    assert result["approval_required"] is True
    assert result["status"] == "approval_required"


def test_surge_below_1_3_is_medium():
    result = classify_action_risk("surge", 1.2)

    assert result["risk_level"] == "medium"
    assert result["approval_required"] is False
    assert result["status"] == "allowed"


def test_surge_at_1_3_requires_approval():
    result = classify_action_risk("surge", 1.3)

    assert result["risk_level"] == "high"
    assert result["approval_required"] is True
    assert result["status"] == "approval_required"


def test_surge_above_2_is_rejected():
    result = classify_action_risk("surge", 2.1)

    assert result["risk_level"] == "high"
    assert result["approval_required"] is False
    assert result["status"] == "rejected"


def test_invalid_surge_is_rejected_with_error():
    with pytest.raises(ValueError):
        classify_action_risk("surge", 0.9)


def test_invalid_incentive_is_rejected_with_error():
    with pytest.raises(ValueError):
        classify_action_risk("incentive", -1)


def test_unknown_action_is_rejected_with_error():
    with pytest.raises(ValueError):
        classify_action_risk("unknown", 10)


def test_policy_allows_standard_surge():
    result = validate_policy_action("SFO", "surge", 1.2)
    assert result["status"] == "allowed"


def test_policy_requires_approval_for_high_surge():
    result = validate_policy_action("SFO", "surge", 1.6)
    assert result["status"] == "approval_required"


def test_policy_rejects_excessive_surge():
    result = validate_policy_action("SFO", "surge", 2.1)
    assert result["status"] == "rejected"


def test_policy_allows_incentive_up_to_25():
    result = validate_policy_action("SFO", "incentive", 25)
    assert result["status"] == "allowed"


def test_policy_requires_approval_above_25():
    result = validate_policy_action("SFO", "incentive", 30)
    assert result["status"] == "approval_required"


def test_human_approval_allows_validated_action():
    validation = validate_policy_action("SFO", "surge", 1.6)
    result = process_human_approval(validation, approved=True)

    assert result["execution_status"] == "approved"
    assert result["approval_decision"] == "approved"


def test_human_denial_blocks_action():
    validation = validate_policy_action("SFO", "surge", 1.6)
    result = process_human_approval(validation, approved=False)

    assert result["execution_status"] == "blocked"
    assert result["approval_decision"] == "denied"


def test_rejected_action_cannot_be_approved():
    validation = validate_policy_action("SFO", "surge", 2.1)
    result = process_human_approval(validation, approved=True)

    assert result["execution_status"] == "blocked"
    assert result["approval_decision"] == "not_applicable"


def test_allowed_action_does_not_need_approval():
    validation = validate_policy_action("SFO", "surge", 1.2)
    result = process_human_approval(validation, approved=False)

    assert result["execution_status"] == "ready"
    assert result["approval_decision"] == "not_required"
