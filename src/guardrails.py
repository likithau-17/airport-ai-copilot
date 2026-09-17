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


def validate_policy_action(
    airport_code: str,
    action_type: str,
    proposed_value: float,
) -> dict:
    """Validate an operational action against airport policy thresholds."""

    airport_code = airport_code.upper()
    action_type = action_type.lower()

    if airport_code not in {"SFO", "LAX", "JFK"}:
        raise ValueError(f"Unknown airport code: {airport_code}")

    if action_type == "surge":
        if proposed_value < 1.0:
            return {
                "airport_code": airport_code,
                "action_type": action_type,
                "status": "rejected",
                "reason": "Surge multiplier cannot be below 1.0x.",
            }

        if proposed_value > 2.0:
            return {
                "airport_code": airport_code,
                "action_type": action_type,
                "status": "rejected",
                "reason": "Surge multiplier exceeds the maximum permitted 2.0x.",
            }

        if proposed_value >= 1.3:
            return {
                "airport_code": airport_code,
                "action_type": action_type,
                "status": "approval_required",
                "reason": "Surge multiplier of 1.3x or higher requires human approval.",
            }

        return {
            "airport_code": airport_code,
            "action_type": action_type,
            "status": "allowed",
            "reason": "Surge multiplier is within the standard operating range.",
        }

    if action_type == "incentive":
        if proposed_value < 0:
            return {
                "airport_code": airport_code,
                "action_type": action_type,
                "status": "rejected",
                "reason": "Incentive cannot be negative.",
            }

        if proposed_value > 25:
            return {
                "airport_code": airport_code,
                "action_type": action_type,
                "status": "approval_required",
                "reason": "Incentives above $25 per eligible driver require human approval.",
            }

        return {
            "airport_code": airport_code,
            "action_type": action_type,
            "status": "allowed",
            "reason": "Incentive is within the medium-impact policy threshold.",
        }

    raise ValueError(f"Unsupported action type: {action_type}")