import pandas as pd
from arxiv import Paper
from tinydb import TinyDB, Query

# Read the entire JSON file (only feasible if you have enough RAM or if you do this in chunks)
# df = pd.read_json('arxiv-metadata-oai-snapshot.json', lines=True)
# df.to_parquet('arxiv-metadata.parquet')
# df = pd.read_parquet('arxiv-metadata.parquet')
# ai = df[df['categories'].str.contains('cs.AI', na=False)]
# # Save the AI papers to a new parquet file
# ai.to_json('arxiv-metadata-ai.json', orient='records', lines=True)

# load the ai papers
ai = pd.read_json('arxiv-metadata-ai.json', lines=True)

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
        published=row['update_date'],
        id=row['id'],
        comments=row['comments'],
        license=row['license'],
        journal_ref=row['journal-ref'],
        report_no=row['report-no'],
        authors_parsed=row['authors_parsed'],
        submitter=row['submitter']
    )

def load_metadata() -> list:
    """
    Load the metadata from the database.
    """
    return [get_paper(row) for index, row in ai.iterrows()]

papers = load_metadata()

db = TinyDB('databases/tinydb/db.json')

def insert_object(obj):
    """ Insert a Python object into the database """
    db.insert(obj)

def search_object(name):
    """ Search for objects by name """
    User = Query()
    return db.search(User.name == name)

# Usage
insert_object({'name': 'John Doe', 'age': 30})  # Example object
result = search_object('John Doe')
print(result)