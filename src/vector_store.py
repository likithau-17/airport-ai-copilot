from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.document_loader import load_policy_documents, split_policy_documents

from google import genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.prompts import build_policy_prompt


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


def get_retriever():
    """Load the saved FAISS index and return a similarity retriever."""
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.load_local(
        str(VECTOR_STORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vector_store.as_retriever(search_kwargs={"k": 3})


def get_retriever():
    """Load the saved FAISS index and return a similarity retriever."""
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.load_local(
        str(VECTOR_STORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vector_store.as_retriever(search_kwargs={"k": 3})


def retrieve_policy_context(question: str) -> str:
    """Retrieve relevant policy chunks and combine them into context."""

    retriever = get_retriever()
    documents = retriever.invoke(question)

    return "\n\n---\n\n".join(
        document.page_content for document in documents
    )


def answer_policy_question(question: str) -> str:
    """Retrieve policy context and generate a grounded Gemini answer."""

    context = retrieve_policy_context(question)
    prompt = build_policy_prompt(question, context)

    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return response.text