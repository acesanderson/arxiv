from Paper import Paper
from pathlib import Path
from arxiv_CRUD import get_paper_by_id, get_all_ids
import requests
from time import sleep
import re

dir_path = Path(__file__).parent
pdfs_path = dir_path / "pdfs"
id_regex = r"^\d+\.\d+$"


def get_url(paper: Paper) -> str:
    url = f"https://arxiv.org/pdf/{paper.arxiv_id}"
    return url


def download_paper(paper: Paper | str) -> None:
    if isinstance(paper, str):
        paper = get_paper_by_id(paper)
    url = get_url(paper)
    pdf_path = pdfs_path / f"{paper.arxiv_id}.pdf"
    if pdf_path.exists():
        print(f"File {pdf_path} already exists. Skipping download.")
        return
    print(f"Downloading {paper.title} from {url}")
    pdf_path.write_bytes(requests.get(url).content)
    print(f"Downloaded {paper.title} to {pdf_path}")


def download_papers(limit: int = 100) -> None:
    all_ids = get_all_ids()
    downloaded_ids = get_downloaded_ids()
    ids_to_download = all_ids - downloaded_ids
    for index in range(limit):
        id = ids_to_download.pop()
        print(f"Downloading paper {index + 1}/{limit}: {id}")
        if not validate_id(id):
            print(f"Invalid ID: {id}")
            continue
        download_paper(id)
        sleep(1)


def get_downloaded_ids() -> set[str]:
    return {pdf_path.stem for pdf_path in pdfs_path.glob("*.pdf")}


def validate_id(paper_id: str) -> bool:
    """
    Validate if the paper ID is in the correct format.
    """
    return bool(re.match(id_regex, paper_id))


def get_a_paper() -> Paper:
    ids = get_downloaded_ids()
    id = ids.pop()
    paper = get_paper_by_id(id)
    return paper


def get_a_filepath() -> str:
    paper = get_a_paper()
    pdf_path = pdfs_path / f"{paper.arxiv_id}.pdf"
    return pdf_path


if __name__ == "__main__":
    # paper = get_a_paper()
    # print(paper.title.replace("\n", ""))
    download_papers(limit=1000)
