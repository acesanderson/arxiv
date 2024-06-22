"""
This script accesses the mongodb database and provides importable query function(s).
"""

from arxiv import Paper
from pymongo import MongoClient
import pymongo

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

"""
Start mongodb server with:

`sudo systemctl start mongod`
"""

# Replace 'localhost' with the IP address of your MongoDB server if it's not on your local machine.
# The default port for MongoDB is 27017. Modify if your setup uses a different port.
client = MongoClient('mongodb://localhost:27017/')
# Creating a new database called 'research'
db = client['research']
# Creating a new collection within the 'research' database called 'papers'
papers_collection = db['papers']




# Close the client connection
client.close()
