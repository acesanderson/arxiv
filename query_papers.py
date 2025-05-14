"""
Command line utility that queries the chroma db for papers related to a given query.
The embeddings are the abstracts.
Upcoming functionality:
- return Paper objects so you can see the authors, categories, etc.
- a function that downloads the paper from arxiv.
- fine-tuning a language model on 90,000+ papers (at 3 seconds a paper, that's 75 hours and ~2 terabytes of data).
"""

import chromadb
import random
import argparse

queries = """
Generating educational materials with large language models
Applications of Natural Language Processing to curriculum development
The role of LLMs in creating educational content
""".strip().split("\n")

# create chroma db
client = chromadb.PersistentClient(path="/home/bianders/Brian_Code/databases/arxiv-vectordb")
collection = client.get_collection("AI_papers_6_15_2024")

def query_papers(query, k = 10):
    """
    Queries the chroma db for the given query.
    """
    results = collection.query(
        query_texts=[query], # Chroma will embed this for you
        n_results=k # how many results to return
    )
    return results

if __name__ == '__main__':
    # Set query to a random query if no query is provided
    query = random.choice(queries)
    # argparse makes this so simple
    parser = argparse.ArgumentParser(description="Example CLI tool using argparse.")
    parser.add_argument('query', type=str, nargs = "?", default=query, help='The search query')
    parser.add_argument('--k', type=int, default=10, help='Number of results to return')
    args = parser.parse_args()
    results = query_db(args.query, k=args.k)
    # Recall that our ids are in the format arxiv_id::title
    titles = [result.split("::")[1] for result in results['ids'][0]]
    print(f"===============================================\nResults for query: {args.query}\n===============================================")
    print("\n".join(titles))
