import streamlit as st

from src.tools import get_airport_metrics, trigger_surge_override

from src.agents import (
    investigate_operations,
    resolve_operations,
    check_policy_compliance,
)

from src.guardrails import (
    validate_policy_action,
    process_human_approval,
    create_audit_record,
    save_audit_record,
)

from src.vector_store import answer_policy_question

from src.memory import ConversationMemory
from src.agents import run_conversation_turn

st.set_page_config(
    page_title="Airport Operations AI Copilot",
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ Airport Operations AI Copilot")
st.caption("Generative AI assistant for airport operations and marketplace analytics")

if "investigation" not in st.session_state:
    st.session_state.investigation = None

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

airport_code = st.selectbox(
    "Select Airport",
    ["SFO", "LAX", "JFK"],
)

metrics = get_airport_metrics(airport_code)

st.subheader("Operational Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Completion Rate",
        f"{metrics['completion_rate']:.0%}",
    )

with col2:
    st.metric(
        "Average ETA",
        f"{metrics['average_eta']:.1f} min",
    )

with col3:
    st.metric(
        "Active Drivers",
        metrics["active_drivers"],
    )

with col4:
    st.metric(
        "Queue Size",
        metrics["queue_size"],
    )

st.subheader("Additional Metrics")

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        "Driver Cancellation Rate",
        f"{metrics['driver_cancellation_rate']:.0%}",
    )

with col6:
    st.metric(
        "Surge Multiplier",
        f"{metrics['surge_multiplier']:.1f}x",
    )

with col7:
    st.metric(
        "Request Volume",
        metrics["request_volume"],
    )

with col8:
    st.metric(
        "Latest Timestamp",
        metrics["timestamp"],
    )

st.subheader("AI Operations Investigation")

if st.button("🔍 Investigate Airport"):
    st.session_state.investigation = investigate_operations(airport_code)

if st.session_state.investigation:
    investigation = st.session_state.investigation

    st.subheader("Agent Activity Trace")

    st.write("1️⃣ Operations Investigator → completed")
    st.write("2️⃣ Policy & Compliance → completed")
    st.write("3️⃣ Resolution → completed")

    st.write(f"**Assessment:** {investigation['assessment']}")

    if investigation["issues"]:
        st.write("**Issues Detected:**")
        for issue in investigation["issues"]:
            st.warning(issue)
    else:
        st.success("No operational issues detected.")

    resolution = resolve_operations(investigation)

    st.write("**Recommended Actions:**")
    for recommendation in resolution["recommendations"]:
        st.info(recommendation)

    if resolution["requires_human_review"]:
        st.warning("⚠️ Human review is required for the current operational condition.")

    if metrics["surge_multiplier"] >= 1.3:
        policy_review = check_policy_compliance(
            airport_code,
            "surge",
            metrics["surge_multiplier"],
        )

        st.write("**Policy & Compliance Review:**")

        if policy_review["status"] == "approval_required":
            st.warning(
                f"⚠️ {policy_review['reason']}"
            )
        elif policy_review["status"] == "rejected":
            st.error(
                f"❌ {policy_review['reason']}"
            )
        else:
            st.success(
                f"✅ {policy_review['reason']}"
            )

        if policy_review["status"] == "approval_required":
            st.write("### Human Approval")

            st.info(
                f"Approval required to apply {metrics['surge_multiplier']:.1f}x surge at {airport_code}."
            )

            approved = st.checkbox(
                "I approve this operational action."
            )

            if approved:
                st.success("✅ Human approval recorded.")

                validation_result = validate_policy_action(
                    airport_code,
                    "surge",
                    metrics["surge_multiplier"],
                )

                approval_result = process_human_approval(
                    validation_result,
                    approved=True,
                )

                execution_result = trigger_surge_override(
                    airport_code,
                    metrics["surge_multiplier"],
                    approved=True,
                )

                audit_record = create_audit_record(
                    airport_code,
                    "surge",
                    metrics["surge_multiplier"],
                    validation_result,
                    approval_result,
                    execution_result["status"],
                )

                save_audit_record(audit_record)

                if execution_result["status"] == "executed":
                    st.success(
                        f"🚀 Surge override executed at "
                        f"{execution_result['surge_multiplier']:.1f}x."
                    )
                    st.write(f"**Execution Result:** {execution_result['reason']}")

                st.write("### Audit Trail")
                st.json(audit_record)

            else:
                st.warning("⏳ Waiting for human approval.")

st.subheader("💬 Operations Assistant")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_query = st.chat_input(
    "Ask about airport operations, metrics, or policy..."
)

if user_query:
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_query,
        }
    )

    conversation = run_conversation_turn(
        st.session_state.memory,
        user_query,
        airport_code,
    )

    resolved_airport = conversation["resolved_airport"]

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching airport policies..."):
                answer = answer_policy_question(
                    f"""
    Previous conversation context:
    {st.session_state.memory.get_history()}

    Current airport:
    {resolved_airport}

    User question:
    {user_query}
    """.strip()
                )
        except Exception as exc:
            answer = (
                "The AI service is temporarily unavailable. "
                "Please try the question again in a moment."
            )
            st.warning(f"AI service error: {exc}")

        st.caption(f"Airport context: {resolved_airport}")

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )