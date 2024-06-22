"""
This script is currently initializing a ChromaDB collection with the AI papers from the arXiv dataset.
These a 90,000 papers.
Key is the arxiv_id + title
Value is the abstract (saved as an embedding)

Goal for this vectordb:
- Create a collection with the AI papers from the arXiv dataset.
- I'll be able to query the database as RAG for the purpose of harvesting prompt templates.
- Ultimately, an experiment to see if a vectordb of this size suits our purposes.
"""

from dataclasses import dataclass

@dataclass
class Paper:
    """
    This maps 1:1 to the Arxiv dataset.
    """
    title: str
    abstract: str
    authors: list
    categories: list
    doi: str
    arxiv_id: str
    update_date: str
    id: str
    comments: str
    license: str
    journal_ref: str
    report_no: str
    authors_parsed: str
    submitter: str

