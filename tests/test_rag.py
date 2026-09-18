from src.vector_store import retrieve_policy_context


def test_sfo_surge_limit_is_retrieved():
    context = retrieve_policy_context(
        "What is the maximum allowed surge multiplier at SFO?"
    )
    assert "2.0x" in context
    assert "SFO" in context


def test_surge_approval_rule_is_retrieved():
    context = retrieve_policy_context(
        "When does surge pricing require human approval?"
    )
    assert "1.3x" in context
    assert "human approval" in context.lower()


def test_incentive_threshold_is_retrieved():
    context = retrieve_policy_context(
        "What is the maximum driver incentive without explicit approval?"
    )
    assert "$25" in context


def test_completion_target_is_retrieved():
    context = retrieve_policy_context(
        "What completion rate target applies to airport operations?"
    )
    assert "90%" in context


def test_retrieval_returns_multiple_policy_chunks():
    context = retrieve_policy_context(
        "What are the airport pricing and operations rules?"
    )
    chunks = [chunk for chunk in context.split("\n\n---\n\n") if chunk.strip()]
    assert len(chunks) >= 2
