import pandas as pd

METRICS_FILE = "data/airport_metrics.csv"


def get_airport_metrics(airport_code: str) -> dict:
    """Return the latest operational metrics for an airport."""

    airport_code = airport_code.upper()

    df = pd.read_csv(METRICS_FILE)
    airport_data = df[df["airport_code"] == airport_code]

    if airport_data.empty:
        raise ValueError(f"Unknown airport code: {airport_code}")

    latest = airport_data.sort_values("timestamp").iloc[-1]

    return {
        "airport_code": latest["airport_code"],
        "completion_rate": float(latest["completion_rate"]),
        "average_eta": float(latest["average_eta"]),
        "active_drivers": int(latest["active_drivers"]),
        "driver_cancellation_rate": float(latest["driver_cancellation_rate"]),
        "queue_size": int(latest["queue_size"]),
        "surge_multiplier": float(latest["surge_multiplier"]),
        "request_volume": int(latest["request_volume"]),
        "timestamp": str(latest["timestamp"]),
    }


def calculate_driver_incentive(
    airport_code: str,
    active_drivers: int,
    request_volume: int,
    queue_size: int,
) -> dict:
    """Calculate a proposed driver incentive based on operational pressure."""

    airport_code = airport_code.upper()

    if airport_code not in {"SFO", "LAX", "JFK"}:
        raise ValueError(f"Unknown airport code: {airport_code}")

    if active_drivers < 0 or request_volume < 0 or queue_size < 0:
        raise ValueError("Operational metrics cannot be negative.")

    driver_gap = request_volume - active_drivers

    if driver_gap <= 0 and queue_size < 30:
        incentive = 0.0
        reason = "Driver supply is sufficient for current demand."
    elif queue_size >= 60 or driver_gap >= 60:
        incentive = 25.0
        reason = "High operational pressure requires the maximum medium-impact incentive."
    elif queue_size >= 30 or driver_gap >= 30:
        incentive = 15.0
        reason = "Moderate operational pressure justifies a driver incentive."
    else:
        incentive = 10.0
        reason = "Some additional driver availability is needed."

    return {
        "airport_code": airport_code,
        "proposed_incentive": incentive,
        "impact_level": "medium" if incentive <= 25 else "high",
        "reason": reason,
    }


def trigger_surge_override(
    airport_code: str,
    surge_multiplier: float,
    approved: bool = False,
) -> dict:
    """Validate and trigger a temporary surge override."""

    airport_code = airport_code.upper()

    if airport_code not in {"SFO", "LAX", "JFK"}:
        raise ValueError(f"Unknown airport code: {airport_code}")

    if surge_multiplier < 1.0:
        raise ValueError("Surge multiplier cannot be below 1.0x.")

    if surge_multiplier > 2.0:
        return {
            "airport_code": airport_code,
            "status": "rejected",
            "surge_multiplier": surge_multiplier,
            "reason": "Requested surge exceeds the maximum permitted 2.0x.",
        }

    if surge_multiplier >= 1.3 and not approved:
        return {
            "airport_code": airport_code,
            "status": "approval_required",
            "surge_multiplier": surge_multiplier,
            "reason": "Surge multiplier of 1.3x or higher requires human approval.",
        }

    return {
        "airport_code": airport_code,
        "status": "executed",
        "surge_multiplier": surge_multiplier,
        "reason": "Surge override approved and triggered.",
    }
