"""
This script accesses the mongodb database and provides importable query function(s).
"""

from arxiv import Paper
from pymongo import MongoClient

# in case user needs a handy list of fields (accessed through metadata.fields)
fields = list(Paper.__dataclass_fields__.keys())

# load the arxiv metadata from the big json file
def get_paper(row):
    """
    Convert a MongoDB document (dictionary) to a Paper object.
    Handles MongoDB fields that do not directly map to Python variable names.
    """
    return Paper(
        title=row.get('title', ''),
        abstract=row.get('abstract', ''),
        authors=row.get('authors', []),
        categories=row.get('categories', []),
        doi=row.get('doi', ''),
        arxiv_id=row.get('id', ''),
        update_date=row.get('update_date', ''),
        id=row.get('id', ''),
        comments=row.get('comments', ''),
        license=row.get('license', ''),
        journal_ref=row.get('journal-ref', ''),
        report_no=row.get('report-no', ''),
        authors_parsed=row.get('authors_parsed', []),
        submitter=row.get('submitter', '')
    )

def get_collection():
	client = MongoClient('mongodb://localhost:27017/')
	db = client['research']
	papers_collection = db['papers']
	return papers_collection

def query_papers(field, keyword):
	"""
	Provide a field and keyword to search for in the MongoDB collection.
	"""
	collection = get_collection()
	query = {field: {'$regex': keyword, '$options': 'i'}}  # Case-insensitive searching
	results = collection.find(query)
	# Convert each MongoDB document (dictionary) back to a Paper dataclass instance
	papers_list = [get_paper(result) for result in results]
	return papers_list

"""
Start mongodb server with:

`sudo systemctl start mongod`
"""

if __name__ == '__main__':
	papers = query_papers('title', 'quantum')
	print(papers[:10])
	paper = query_papers('id', '0812.4614')
	print(paper)

