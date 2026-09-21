# Airport Operations AI Copilot

An end-to-end **Generative AI copilot for airport operations and marketplace analytics**.

The system combines **RAG, embeddings, FAISS vector search, operational tools, agent-style orchestration, conversational memory, guardrails, human approval, audit logging, and a Streamlit interface**.

---

## Architecture

```text
User Query
    ↓
Airport Context + Conversation Memory
    ↓
RAG Retrieval
    ↓
Policy Context
    ↓
Operations Investigation
    ↓
Policy & Compliance
    ↓
Resolution / Recommendation
    ↓
Risk Classification
    ↓
Human Approval (when required)
    ↓
Guarded Execution
    ↓
Audit Trail
```

---

## Key Features

* **RAG pipeline** using policy documents, Sentence Transformers embeddings, and FAISS.
* **Policy-grounded answers** using source-aware retrieval context.
* **Operational metrics** for SFO, LAX, and JFK.
* **Operational tools**:

  * `get_airport_metrics`
  * `calculate_driver_incentive`
  * `trigger_surge_override`
* **Agent-style workflow**:

  * Operations Investigator
  * Policy & Compliance
  * Resolution
* **Conversation memory** for follow-up questions, including references such as `"it"` when referring to a previously discussed airport.
* **Controlled agent loop** with a maximum of 5 iterations.
* **Guardrails and risk classification** for operational actions.
* **Human-in-the-loop approval** for high-impact actions.
* **Policy validation** before execution.
* **Audit trail** for guarded actions.
* **Distilled training data** stored in JSONL format.
* **Streamlit UI** with chat, operational metrics, agent activity, and approval flow.

---

## Policy Guardrails

| Action                  | Rule                    |
| ----------------------- | ----------------------- |
| Metrics / policy lookup | Low risk, no approval   |
| Driver incentive ≤ $25  | Medium impact           |
| Driver incentive > $25  | Human approval required |
| Surge < 1.3x            | Medium risk             |
| Surge ≥ 1.3x            | Human approval required |
| Surge > 2.0x            | Rejected                |

---

## Project Structure

```text
airport-ai-copilot/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── app.py
│
├── data/
│   ├── airport_policies/
│   └── airport_metrics.csv
│
├── notebooks/
│   ├── day1_rag_pipeline.ipynb
│   ├── day2_tools.ipynb
│   ├── day3_agents.ipynb
│   └── day4_guardrails.ipynb
│
├── src/
│   ├── config.py
│   ├── document_loader.py
│   ├── vector_store.py
│   ├── tools.py
│   ├── agents.py
│   ├── memory.py
│   ├── guardrails.py
│   └── prompts.py
│
├── output/
│   └── distilled_training_data.jsonl
│
└── tests/
    ├── test_rag.py
    ├── test_tools.py
    ├── test_agents.py
    ├── test_memory.py
    └── test_guardrails.py
```

---

## Setup

### 1. Create and Activate a Virtual Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Gemini API Key

Create `.env` from `.env.example` and add your Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here
```

---

## Build the FAISS Index

From the repository root:

```bash
python -m src.vector_store
```

This process:

1. Reads the airport policy documents.
2. Splits the documents into chunks.
3. Generates embeddings using Sentence Transformers.
4. Builds the FAISS vector index.
5. Stores the generated vector store under:

```text
data/faiss_index/
```

---

## Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application provides an interactive airport operations copilot for **SFO, LAX, and JFK**.

---

## Example Queries

```text
What is the maximum allowed surge multiplier at SFO?
```

```text
What is happening at SFO?
```

```text
What about it now?
```

```text
When does surge pricing require human approval?
```

```text
Can we provide a $30 driver incentive?
```

```text
What are the current operational metrics at LAX?
```

---

## Testing

Run the complete test suite:

```bash
python -m pytest -q
```

The project contains dedicated tests for:

* RAG retrieval
* Operational tools
* Agent orchestration
* Conversation memory
* Guardrails
* Human approval workflows

---

## Notebooks

The notebooks document the development stages of the project.

### Day 1 — RAG Pipeline

`day1_rag_pipeline.ipynb`

Covers:

* Document loading
* Text chunking
* Embedding generation
* FAISS index creation
* Similarity retrieval
* Policy-grounded answers

### Day 2 — Operational Tools

`day2_tools.ipynb`

Covers:

* Airport operational metrics
* Driver incentive calculations
* Surge override functionality
* Deterministic operational tools

### Day 3 — Agent Orchestration

`day3_agents.ipynb`

Covers:

* Agent orchestration
* Controlled agent loops
* Tool selection
* Conversation memory
* Follow-up question handling

### Day 4 — Guardrails

`day4_guardrails.ipynb`

Covers:

* Risk classification
* Policy validation
* Human approval
* Guarded execution
* Audit records

---

## Technology Stack

* Python
* Pandas
* LangChain
* Sentence Transformers
* FAISS
* Google Gemini
* Streamlit
* Pytest
* Git / GitHub

---

## Safety and Governance

The copilot separates **recommendations from execution**.

Actions that cross defined policy thresholds are not automatically executed. Instead, they are:

1. Classified according to risk.
2. Validated against the applicable policy.
3. Routed for human approval when required.
4. Executed only after the required approval.
5. Recorded in an audit trail for traceability.

Requests that exceed hard policy limits are rejected rather than executed.

This approach provides a controlled workflow for operational AI actions while maintaining human oversight for higher-impact decisions.

---

## Project Status

The project implements the planned **Airport Operations AI Copilot prototype**, including:

1. RAG and policy Q&A
2. Operational tools
3. Agent orchestration
4. Conversation memory
5. Guardrails
6. Human-in-the-loop approval
7. Audit logging
8. Distilled training data
9. Streamlit application
10. Automated testing
