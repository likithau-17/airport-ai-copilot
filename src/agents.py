from src.tools import get_airport_metrics


def investigate_operations(airport_code: str) -> dict:
    """Investigate the latest operational condition at an airport."""

    metrics = get_airport_metrics(airport_code)

    issues = []

    if metrics["completion_rate"] < 0.90:
        issues.append("completion rate is below the 90% target")

    if metrics["driver_cancellation_rate"] >= 0.10:
        issues.append("driver cancellation rate is at or above 10%")

    if metrics["queue_size"] >= 50:
        issues.append("driver queue size is high")

    if metrics["surge_multiplier"] >= 1.3:
        issues.append("surge pricing is currently elevated")

    if issues:
        assessment = "Operational degradation detected."
    else:
        assessment = "Airport operations are within normal thresholds."

    return {
        "airport_code": metrics["airport_code"],
        "assessment": assessment,
        "issues": issues,
        "metrics": metrics,
    }


def check_policy_compliance(
    airport_code: str,
    action_type: str,
    proposed_value: float,
) -> dict:
    """Check whether an operational action requires approval."""

    airport_code = airport_code.upper()

    if airport_code not in {"SFO", "LAX", "JFK"}:
        raise ValueError(f"Unknown airport code: {airport_code}")

    action_type = action_type.lower()

    if action_type == "surge":
        if proposed_value > 2.0:
            return {
                "airport_code": airport_code,
                "action_type": action_type,
                "status": "rejected",
                "approval_required": False,
                "reason": "Surge multiplier exceeds the maximum permitted 2.0x.",
            }

        if proposed_value >= 1.3:
            return {
                "airport_code": airport_code,
                "action_type": action_type,
                "status": "approval_required",
                "approval_required": True,
                "reason": "Surge multiplier of 1.3x or higher requires human approval.",
            }

    elif action_type == "incentive":
        if proposed_value > 25:
            return {
                "airport_code": airport_code,
                "action_type": action_type,
                "status": "approval_required",
                "approval_required": True,
                "reason": "Incentives above $25 per eligible driver require human approval.",
            }

    else:
        raise ValueError(f"Unsupported action type: {action_type}")

    return {
        "airport_code": airport_code,
        "action_type": action_type,
        "status": "allowed",
        "approval_required": False,
        "reason": "Action is within the defined policy threshold.",
    }


def resolve_operations(investigation: dict) -> dict:
    """Create an operational recommendation from investigation results."""

    airport_code = investigation["airport_code"]
    issues = investigation["issues"]
    metrics = investigation["metrics"]

    recommendations = []

    if metrics["queue_size"] >= 50:
        recommendations.append(
            "Recommend repositioning drivers to approved staging areas."
        )

    if metrics["driver_cancellation_rate"] >= 0.10:
        recommendations.append(
            "Investigate elevated driver cancellation activity."
        )

    if metrics["completion_rate"] < 0.90:
        recommendations.append(
            "Investigate service reliability degradation."
        )

    if metrics["surge_multiplier"] >= 1.3:
        recommendations.append(
            "Review the current surge level against pricing policy."
        )

    if not recommendations:
        recommendations.append(
            "No immediate operational intervention is required."
        )

    return {
        "airport_code": airport_code,
        "issues_identified": len(issues),
        "recommendations": recommendations,
        "requires_human_review": metrics["surge_multiplier"] >= 1.3,
    }


def orchestrate_operations(airport_code: str) -> dict:
    """Coordinate investigation, policy review, and resolution."""

    investigation = investigate_operations(airport_code)

    resolution = resolve_operations(investigation)

    policy_review = None

    if investigation["metrics"]["surge_multiplier"] >= 1.3:
        policy_review = check_policy_compliance(
            airport_code,
            "surge",
            investigation["metrics"]["surge_multiplier"],
        )

    return {
        "airport_code": airport_code.upper(),
        "investigation": investigation,
        "policy_review": policy_review,
        "resolution": resolution,
    }


def run_conversation_turn(
    memory,
    user_message: str,
    airport_code: str | None = None,
) -> dict:
    """Run an operations request using conversation memory."""

    resolved_airport = memory.resolve_airport(airport_code)
    memory.update(user_message, resolved_airport)

    result = orchestrate_operations(resolved_airport)
    result["user_message"] = user_message
    result["resolved_airport"] = resolved_airport

    return result


def run_controlled_agent_loop(airport_code: str, max_iterations: int = 5) -> dict:
    """Run a bounded operations reasoning loop."""

    if max_iterations < 1:
        raise ValueError("max_iterations must be at least 1.")

    max_iterations = min(max_iterations, 5)
    steps = []

    investigation = investigate_operations(airport_code)
    steps.append(
        {
            "iteration": 1,
            "agent": "Operations Investigator",
            "action": "investigate_operations",
            "status": "completed",
        }
    )

    policy_review = None
    if investigation["metrics"]["surge_multiplier"] >= 1.3 and len(steps) < max_iterations:
        policy_review = check_policy_compliance(
            airport_code,
            "surge",
            investigation["metrics"]["surge_multiplier"],
        )
        steps.append(
            {
                "iteration": 2,
                "agent": "Policy & Compliance",
                "action": "check_policy_compliance",
                "status": policy_review["status"],
            }
        )

    resolution = None
    if len(steps) < max_iterations:
        resolution = resolve_operations(investigation)
        steps.append(
            {
                "iteration": len(steps) + 1,
                "agent": "Resolution",
                "action": "resolve_operations",
                "status": "completed",
            }
        )

    return {
        "airport_code": airport_code.upper(),
        "iterations": len(steps),
        "max_iterations": max_iterations,
        "steps": steps,
        "investigation": investigation,
        "policy_review": policy_review,
        "resolution": resolution,
    }


from src.vector_store import retrieve_policy_context


def retrieve_policy_for_agent(question: str) -> dict:
    """Retrieve relevant airport policy context for an agent decision."""

    context = retrieve_policy_context(question)

    return {
        "question": question,
        "context": context,
        "source_count": len(
            [section for section in context.split("\n\n---\n\n") if section.strip()]
        ),
    }
