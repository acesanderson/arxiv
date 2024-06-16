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

import pandas as pd
import chromadb
from dataclasses import dataclass

# Read the entire JSON file (only feasible if you have enough RAM or if you do this in chunks)
# df = pd.read_json('arxiv-metadata-oai-snapshot.json', lines=True)
# df.to_parquet('arxiv-metadata.parquet')
# df = pd.read_parquet('arxiv-metadata.parquet')
# ai = df[df['categories'].str.contains('cs.AI', na=False)]
# # Save the AI papers to a new parquet file
# ai.to_json('arxiv-metadata-ai.json', orient='records', lines=True)

# load the ai papers
ai = pd.read_json('arxiv-metadata-ai.json', lines=True)

# create chroma db
client = chromadb.PersistentClient(path="vectordbs/arxiv")
# collection = client.create_collection("AI_papers_6_15_2024")
collection = client.get_collection("AI_papers_6_15_2024")

@dataclass
class Paper:
    title: str
    abstract: str
    authors: list
    categories: list
    doi: str
    arxiv_id: str
    published: str

def get_paper(row):
    """
    Converts a row in our DataFrame to a Paper object.
    """
    return Paper(
        title=row['title'],
        abstract=row['abstract'],
        authors=row['authors'],
        categories=row['categories'],
        doi=row['doi'],
        arxiv_id=row['id'],
        published=row['update_date']
    )

def create_keys_and_values(paper):
    """
    Creates the key and value for the document in the chroma collection.
    """
    key = paper.arxiv_id + "::" + paper.title
    value = paper.title + "::" + paper.abstract
    return key, value


# Since we have 90,000 records ... this is likely to break a few times.
# So we will keep track of where we are at.

def save_progress(index):
    """
    Saves the index of the last paper processed to a file.
    """
    with open("last_index.txt", "w") as f:
        f.write(str(index))

def load_progress():
    """
    Loads the index of the last paper processed from a file.
    Implementing this in case the script breaks and we need to resume.
    """
    try:
        with open("last_index.txt", "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 0  # if no file exists, start from the beginning

if __name__ == '__main__':
    start_index = load_progress()

    for index, row in ai.iterrows():
        if index < start_index:
            continue  # skip to the point we restarted
        paper = get_paper(row)
        key, value = create_keys_and_values(paper)
        collection.add(documents=[value], ids=[key])
        print(f"Processed paper {index} of {len(ai)}:\t\t{key}")
        save_progress(index)
