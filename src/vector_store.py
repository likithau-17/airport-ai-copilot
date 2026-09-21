from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.document_loader import load_policy_documents, split_policy_documents

from google import genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.prompts import build_policy_prompt

from functools import lru_cache


VECTOR_STORE_DIR = Path("data/faiss_index")


def build_vector_store() -> FAISS:
    """Build a FAISS index from airport policy documents."""
    documents = load_policy_documents()
    chunks = split_policy_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(str(VECTOR_STORE_DIR))

    return vector_store


if __name__ == "__main__":
    store = build_vector_store()
    print(f"FAISS index created with {store.index.ntotal} vectors")


@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def get_retriever():
    """Load the saved FAISS index and return a similarity retriever."""
    embeddings = get_embeddings()

    vector_store = FAISS.load_local(
        str(VECTOR_STORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vector_store.as_retriever(search_kwargs={"k": 3})


def retrieve_policy_context(question: str, airport_code: str | None = None) -> str:
    """Retrieve relevant policy chunks, optionally filtered to one airport."""

    retriever = get_retriever()
    documents = retriever.invoke(question)

    if airport_code:
        airport_code = airport_code.lower()
        documents = [
            document
            for document in documents
            if document.metadata.get("filename", "").lower().startswith(airport_code)
        ]

    sections = []

    for document in documents:
        source = document.metadata.get("filename") or document.metadata.get(
            "source",
            "unknown",
        )

        sections.append(
            f"Source: {source}\n"
            f"Relevant Policy:\n{document.page_content}"
        )

    return "\n\n---\n\n".join(sections)

def answer_policy_question_with_sources(
    question: str,
    airport_code: str | None = None,
) -> tuple[str, list[str]]:
    """Generate a grounded policy answer and return retrieved source filenames."""

    retriever = get_retriever()
    documents = retriever.invoke(question)

    if airport_code:
        airport_code = airport_code.lower()
        documents = [
            document
            for document in documents
            if document.metadata.get("filename", "").lower().startswith(airport_code)
        ]

    context = "\n\n---\n\n".join(
        f"Source: {document.metadata.get('filename', 'unknown')}\n"
        f"Relevant Policy:\n{document.page_content}"
        for document in documents
    )

    sources = list(
        dict.fromkeys(
            document.metadata.get("filename", "unknown")
            for document in documents
        )
    )

    prompt = build_policy_prompt(question, context)

    client = genai.Client(api_key=GEMINI_API_KEY)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text, sources
    except Exception:
        return (
            "The AI service is temporarily unavailable. "
            "The retrieved policy context is available, but the language model "
            "could not generate a response right now.",
            sources,
        )

def answer_policy_question(question: str) -> str:
    """Retrieve policy context and generate a grounded Gemini answer."""

    context = retrieve_policy_context(question, airport_code)
    prompt = build_policy_prompt(question, context)

    client = genai.Client(api_key=GEMINI_API_KEY)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception:
        return (
            "The AI service is temporarily unavailable. "
            "The retrieved policy context is available, but the language model "
            "could not generate a response right now."
        )