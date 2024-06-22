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

def load_metadata() -> list:
    """
    Load the metadata from the database.
    """
    return [get_paper(row) for index, row in ai.iterrows()]

papers = load_metadata()
