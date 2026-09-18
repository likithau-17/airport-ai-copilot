from pathlib import Path
from langchain_core.documents import Document


POLICY_DIR = Path("data/airport_policies")


def load_policy_documents() -> list[Document]:
    """Load all airport policy markdown files as LangChain documents."""
    documents = []

    for file_path in sorted(POLICY_DIR.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(file_path),
                    "filename": file_path.name,
                },
            )
        )

    return documents


def split_policy_documents(documents: list[Document]) -> list[Document]:
    """Split policy documents into retrieval-friendly chunks."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )

    return splitter.split_documents(documents)
