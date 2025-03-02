"""
Abstracts for all of the AI papers in the arxiv dataset (n=11k+). 
Getter functions are provided to get paper titles from chroma collection.

NOTE: Chroma needs to be running on port 8001. This code defaults to localhost.
On Caruana:
```bash
chroma run --port 8001 --path /home/bianders/Databases/chroma
```
"""

import asyncio
from asyncio import Semaphore
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from Paper import Paper
from arxiv_CRUD import get_all_papers, get_paper_by_id
from rich.console import Console
import argparse
import sys

console = Console(width=140)
ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2", device="cuda")


# Our locator functions -- for generating and parsing the ids
def generate_locator(paper: Paper) -> str:
    """
    The ids will be a locator containing information on the location of the video.
    Naming voncention: paper_id:paper_title
    """
    paper_id = paper.arxiv_id
    paper_title = paper.title
    return f"{paper_id}:{paper_title}"


def parse_locator(locator: str) -> tuple[str, str] | None:
    """
    For a given locator, return a tuple with the course title, section title, and video title.
    """
    paper_id = locator.split(":")[0]
    paper = get_paper_by_id(paper_id)
    return paper


# Data prep
def prep_paper(paper: Paper) -> tuple[str, str]:
    """
    Wrapper function that handles inserting all the docs/ids for a course.
    """
    id = generate_locator(paper)
    doc = paper.abstract
    return id, doc


def prep_papers() -> list[tuple]:
    """
    Wrapper function that handles inserting all the docs/ids for all courses.
    """
    papers = get_all_papers()
    items = []
    for paper in papers:
        id, doc = prep_paper(paper)
        items.append((id, doc))
    return items


# Chroma functions
async def load_batch(collection, batch_items: tuple, sem: Semaphore):
    async with sem:
        i, items = batch_items
        print(f"Batch #{i+1}...")
        for item in items:
            await collection.add(
                documents=[item[1]],
                ids=[str(item[0])],
            )
        print(f"Loaded #{i+1}.")


async def heartbeat(client):
    try:
        _ = await client.heartbeat()
        print("Chroma server found.")
    except ValueError as e:
        # Handle tenant/database connection issues
        print(f"Database connection error: {e}")
        raise Exception(f"ChromaDB connection failed - {str(e)}")


async def load_papers_into_chroma():
    # Create a semaphore to limit the number of concurrent requests
    sem = Semaphore(10)
    # Load our client and collection
    client = await chromadb.AsyncHttpClient(port=8001)
    try:
        await client.delete_collection(name="arxiv_abstracts")
    except:
        pass
    collection = await client.create_collection(
        name="arxiv_abstracts", embedding_function=ef
    )
    # Generate the items to load
    items = prep_papers()
    # Batch items into chunks of 100; enumerate them so we can pass the index to the coroutine
    chunks: list[tuple] = list(
        enumerate([items[i : i + 100] for i in range(0, len(items), 100)])
    )
    print(f"Loading {len(chunks)} batches of paper abstracts into Chroma...")
    coroutines = [load_batch(collection, chunk, sem) for chunk in chunks]
    await asyncio.gather(*coroutines)


async def query_papers(query: str, num_results: int = 5):
    client = await chromadb.AsyncHttpClient(port=8001)
    collection = await client.get_collection(
        name="arxiv_abstracts", embedding_function=ef
    )
    results = await collection.query(query_texts=[query])
    results = results["ids"][0]
    results = [parse_locator(result) for result in results]
    return results


def query_video_transcripts_sync(query: str, num_results: int = 5):
    results = asyncio.run(query_papers(query, num_results))
    return results


def pretty_print_results(results):
    for result in results:
        console.print(
            f"[green]{result.arxiv_id:<10}[/green]\t[cyan]{result.title}[/cyan]"
        )


# async def main():
#     client = await chromadb.AsyncHttpClient(port=8001)
#     await heartbeat(client)
#     await load_papers_into_chroma()


# if __name__ == "__main__":
#     asyncio.run(main())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Similarity search for Arxiv paper abstracts."
    )
    # One positional argument: query
    parser.add_argument(
        "query",
        type=str,
        help="Query the arxiv paper abstracts for a given string.",
    )
    args = parser.parse_args()
    if args.query:
        results = query_video_transcripts_sync(args.query)
        pretty_print_results(results)
    else:
        sys.exit()
