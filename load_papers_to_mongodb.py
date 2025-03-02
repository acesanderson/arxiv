"""
This script loads the metadata from the big json file and writes it to a MongoDB database.
Only use when refreshing the dataset from kaggle.
"""

import pandas as pd
from arxiv import Paper
from pymongo import MongoClient
import pymongo


# load the arxiv metadata from the big json file
def get_paper(row):
    """
    Covert json object to Paper object.
    """
    return Paper(
        title=row["title"],
        abstract=row["abstract"],
        authors=row["authors"],
        categories=row["categories"],
        doi=row["doi"],
        arxiv_id=row["id"],
        update_date=row["update_date"],
        id=row["id"],
        comments=row["comments"],
        license=row["license"],
        journal_ref=row["journal-ref"],
        report_no=row["report-no"],
        authors_parsed=row["authors_parsed"],
        submitter=row["submitter"],
    )


def load_metadata() -> list:
    """
    Legacy function. Load the metadata from the big json file.
    """
    return [get_paper(row) for index, row in ai.iterrows()]


def load_paper(paper: Paper):
    """
    Load a Paper object into the MongoDB collection.
    This should upsert the paper if it already exists.
    """
    papers_collection = db["papers"]
    paper_dict = paper.dict()
    papers_collection.update_one(
        {"id": paper_dict["id"]},
        {"$set": paper_dict},
        upsert=True,
    )


# load our dataset from the big json file -- this is legacy and will be removed once we are comfortable with our tinydb database.
ai = pd.read_json("arxiv-metadata-oai-snapshot.json", lines=True)


papers = load_metadata()
# Filter for cs.AI
AI_papers = []
for paper in papers:
    if "cs.AI" in paper.categories:
        AI_papers.append(paper)

client = MongoClient("mongodb://localhost:27017/")

# Creating a new database called 'research'
db = client["arxiv"]

# Creating a new collection within the 'research' database called 'papers'
papers_collection = db["papers"]

# Load all the Paper objects into the MongoDB collection
for index, paper in enumerate(AI_papers):
    load_paper(paper)
    if index % 1000 == 0:
        print(f"Inserted {index} papers")

# Close the client connection
client.close()
