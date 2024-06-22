"""
Use SQLite to load the metadata from the database.
Right now, we are making the database.
"""

import pandas as pd
from arxiv import Paper
import sqlite3
import json

# load our dataset from the big json file -- this is legacy and will be removed once we are comfortable with our tinydb database.
ai = pd.read_json('arxiv-metadata-ai.json', lines=True)
# in case user needs a handy list of fields (accessed through metadata.fields)
fields = list(Paper.__dataclass_fields__.keys())

# load the arxiv metadata from the big json file
def get_paper(row):
    """
    Legacy function; only useful in converting json into Paper objects.
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
    Legacy function. Load the metadata from the big json file.
    Use the TinyDB database instead.
    """
    return [get_paper(row) for index, row in ai.iterrows()]

def write_progress(index: int):
    """
    Simple function to write the progress to a file.
    We have 90k records to process, so we can address errors.
    """
    with open('progress.txt', 'w') as f:
        f.write(str(index))

def load_progress() -> int:
    """
    Simple function to read the progress from a file.
    Useful for restarting if we have errors.
    """
    try:
        with open('progress.txt', 'r') as f:
            return int(f.read())
    except:
        print("Progress file not created yet.")

if __name__ == '__main__':
    print("Loading papers from json object.")
    papers = load_metadata()
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('databases/papers_sqlite/papers.db')
    cursor = conn.cursor()
    cursor.execute('''
CREATE TABLE IF NOT EXISTS papers (
    id TEXT PRIMARY KEY,
    data JSON
)
''')
    index = load_progress()
    try:
        for index, paper in enumerate(papers):
            print(f'Processing paper {index+1} of {len(papers)}')
            # Convert the dictionary to a JSON string
            json_data = json.dumps(paper.__dict__)
            cursor.execute('INSERT INTO papers (id, data) VALUES (?, ?)', (paper.id, json_data))
    except:
        write_progress(index)
        conn.commit()
        conn.close()
        raise

