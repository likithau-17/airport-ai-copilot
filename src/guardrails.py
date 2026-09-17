def classify_action_risk(action_type: str, value: float = 0.0) -> dict:
    """Classify an operational action according to guardrail policy."""

    action_type = action_type.lower()

    if action_type in {"metrics", "policy_lookup"}:
        return {
            "risk_level": "low",
            "approval_required": False,
            "status": "allowed",
        }

    if action_type == "incentive":
        if value < 0:
            raise ValueError("Incentive cannot be negative.")

        if value > 25:
            return {
                "risk_level": "high",
                "approval_required": True,
                "status": "approval_required",
            }

        return {
            "risk_level": "medium",
            "approval_required": False,
            "status": "allowed",
        }

    if action_type == "surge":
        if value < 1.0:
            raise ValueError("Surge multiplier cannot be below 1.0x.")

        if value > 2.0:
            return {
                "risk_level": "high",
                "approval_required": False,
                "status": "rejected",
            }

        if value >= 1.3:
            return {
                "risk_level": "high",
                "approval_required": True,
                "status": "approval_required",
            }

        return {
            "risk_level": "medium",
            "approval_required": False,
            "status": "allowed",
        }

    raise ValueError(f"Unsupported action type: {action_type}")
