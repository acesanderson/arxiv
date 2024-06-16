from arxiv import Paper
import chromadb
import sys

# create chroma db
client = chromadb.PersistentClient(path="vectordbs/arxiv")
collection = client.get_collection("AI_papers_6_15_2024")

def query_db(query):
    """
    Queries the chroma db for the given query.
    """
    results = collection.query(
        query_texts=["This is a query document about hawaii"], # Chroma will embed this for you
        n_results=10 # how many results to return
    )
    return results    

if __name__ == '__main__':
    query = "Metaprompting"
    if len(sys.argv) > 1:
        query = sys.argv[1]
    results = query_db("Metaprompting")
    titles = [result.split("::")[0] for result in results]
    print(titles)
