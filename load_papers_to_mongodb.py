"""
This script loads the metadata from the big json file and writes it to a MongoDB database.
Only use when refreshing the dataset from kaggle.
"""

import pandas as pd
from arxiv import Paper

# load our dataset from the big json file -- this is legacy and will be removed once we are comfortable with our tinydb database.
ai = pd.read_json('arxiv-metadata-ai.json', lines=True)
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
        update_date=row['update_date'],
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


papers = load_metadata()

"""
Start mongodb server with:
`sudo systemctl start mongod`
"""

from pymongo import MongoClient
import pymongo

# Replace 'localhost' with the IP address of your MongoDB server if it's not on your local machine.
# The default port for MongoDB is 27017. Modify if your setup uses a different port.
client = MongoClient('mongodb://localhost:27017/')

# Creating a new database called 'research'
db = client['research']

# Creating a new collection within the 'research' database called 'papers'
papers_collection = db['papers']

# to clear collection if needed
# papers_collection.delete_many({})

# Assume 'papers' is your list of 90,000 JSON objects
# If 'papers' is not yet defined, you need to define it or load it from your source
# For example:
# papers = [{'title': 'Paper 1', 'abstract': 'Abstract 1', ...}, {...}, ...]
papers_dicts = [paper.__dict__ for paper in papers]

# Inserting the papers into the collection
# This method is suitable for a large number of documents as it uses bulk insertion
try:
    result = papers_collection.insert_many(papers_dicts)
    print(f"Inserted {len(result.inserted_ids)} papers")
except pymongo.errors.BulkWriteError as e:
    print("An error occurred while inserting papers:", e.details)

# Verify insertion
print("Number of papers in the database:", papers_collection.count_documents({}))

# Close the client connection
client.close()
