"""
This is a placeholder with some of my old scripts that I used to process and load the big json file of arxiv papers from Kaggle.
"""

import pandas as pd
from arxiv import Paper

# load our dataset from the big json file -- this is legacy and will be removed once we are comfortable with our tinydb database.
ai = pd.read_json('arxiv-metadata-ai.json', lines=True)

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
