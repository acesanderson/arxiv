"""
Use SQLite to load the metadata from the database.
Right now, we are making the database.
"""

import pandas as pd
from arxiv import Paper
import sqlite3
import json

# load our dataset from the big json file -- this is legacy and will be removed once we are comfortable with our tinydb database.
# ai = pd.read_json('arxiv-metadata-ai.json', lines=True)
# in case user needs a handy list of fields (accessed through metadata.fields)
fields = list(Paper.__dataclass_fields__.keys())

# load the arxiv metadata from the big json file
def get_paper(row):
    """
    Covert json object to Paper object.
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

def load_json1_extension(conn):
    # Enable extension loading
    conn.enable_load_extension(True)
    try:
        # Attempt to load the JSON1 extension
        # The actual path to the extension may vary depending on your installation
        # This is an example path; you'll need to provide the correct path for your system
        conn.load_extension('libsqlitefunctions.so')
        # If no error occurs, the extension is successfully loaded
        print("JSON1 extension loaded successfully.")
    except sqlite3.OperationalError as e:
        print(f"Failed to load JSON1 extension: {e}")
    # Disable extension loading for security
    conn.enable_load_extension(False)
    return conn

def query_papers(keyword):
    """
    Searches the SQLite database for papers with a title containing the keyword.
    """
    # Enable SQLite JSON extension
    conn = sqlite3.connect('databases/papers_sqlite/papers.db')
    cursor = conn.cursor()
    # Load json extension
    conn = load_json1_extension(conn)
    # Query to find papers where the title contains the keyword
    query = """
    SELECT data
    FROM papers
    WHERE json_extract(data, '$.title') LIKE ?
    """
    cursor.execute(query, ('%' + keyword + '%',))
    # Fetch all matching records
    results = cursor.fetchall()
    # Close the connection
    conn.close()
    # Return the list of matching JSON objects
    return [json.loads(result[0]) for result in results]

# if __name__ == '__main__':
# print("Loading papers from json object.")
# papers = load_metadata()
# Connect to SQLite database (or create it if it doesn't exist)

query_papers('BART')
