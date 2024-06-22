import pandas as pd
from arxiv import Paper
from tinydb import TinyDB, Query

# load our dataset from the big json file -- this is legacy and will be removed once we are comfortable with our tinydb database.
ai = pd.read_json('arxiv-metadata-ai.json', lines=True)
# load our tinydb database
db = TinyDB('databases/tinydb/papers.json')
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

def query_metadata(query: str, field: str = "title", no_results = None) -> list:
    """
    Query the metadata using a search term.
    To get a list of fields, access metadata.fields (it's a list).
    """
    User = Query()
    results = db.search(User[field] == query)
    return results[:no_results]

papers = load_metadata()


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

for index, paper in enumerate(papers):
    print(f"Inserting paper {index + 1} of {len(papers)}")
    insert_object(paper.__dict__)


# ai = pd.read_json('arxiv-metadata-ai.json', lines=True)
