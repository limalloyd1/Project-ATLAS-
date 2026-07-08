import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import trafilatura # type: ignore 


INPUT_FILE = Path("/home/limalima/AtlasProj/Argus/data/filtered/filteredLinks.txt")
RAW_HTML_DIR = Path("/home/limalima/AtlasProj/Argus/data/raw/learnopengl/html")
PROCESSED_DIR = Path("/home/limalima/AtlasProj/Argus/data/processed/learnopengl/documents")
LOG_FILE = Path("/home/limalima/AtlasProj/Argus/data/logs/ingestion.log")


def ensure_directories():
    RAW_HTML_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def make_document_id(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if not path:
        path = "home"

    slug = path.replace("/", "_")
    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", slug)
    return f"learnopengl_{slug.lower()}"


def log_message(message: str):
    with open(LOG_FILE, "a", encoding="utf-8") as logfile:
        logfile.write(message + "\n")


def read_urls(filename: Path) -> list[str]:
    try:
        with open(filename, "r", encoding="utf-8") as infile:
            return [line.strip() for line in infile if line.strip()]
    except Exception as e:
        print(f"Error reading URL file: {e}")
        return []


def save_raw_html(document_id: str, html: str):
    html_path = RAW_HTML_DIR / f"{document_id}.html"
    with open(html_path, "w", encoding="utf-8") as outfile:
        outfile.write(html)


def save_document_json(document: dict):
    json_path = PROCESSED_DIR / f"{document['document_id']}.json"
    with open(json_path, "w", encoding="utf-8") as outfile:
        json.dump(document, outfile, indent=4, ensure_ascii=False)


def extract_page(url: str, downloaded_html: str):
    extracted_text = trafilatura.extract(
        downloaded_html,
        url=url,
        output_format="txt",
        with_metadata=False,
        favor_precision=True
    )

    extracted_json = trafilatura.extract(
        downloaded_html,
        url=url,
        output_format="json",
        with_metadata=True,
        favor_precision=True
    )

    return extracted_text, extracted_json


def ingest_url(url: str):
    document_id = make_document_id(url)

    try:
        downloaded_html = trafilatura.fetch_url(url)

        if not downloaded_html:
            log_message(f"FAILED_DOWNLOAD | {url}")
            print(f"Failed to download: {url}")
            return

        save_raw_html(document_id, downloaded_html)

        extracted_text, extracted_json = extract_page(url, downloaded_html)

        if not extracted_text:
            log_message(f"FAILED_EXTRACTION | {url}")
            print(f"Failed to extract text: {url}")
            return

        metadata = {}
        if extracted_json:
            try:
                metadata = json.loads(extracted_json)
            except json.JSONDecodeError:
                metadata = {}

        document = {
            "document_id": document_id,
            "source": "LearnOpenGL",
            "url": url,
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "date": metadata.get("date", ""),
            "sitename": metadata.get("sitename", ""),
            "source_type": "webpage",
            "extractor": "trafilatura",
            "raw_html_path": str(RAW_HTML_DIR / f"{document_id}.html"),
            "text": extracted_text,
            "status": "success"
        }

        save_document_json(document)
        log_message(f"SUCCESS | {url}")
        print(f"Ingested: {url}")

    except Exception as e:
        log_message(f"ERROR | {url} | {e}")
        print(f"Error processing {url}: {e}")


def main():
    ensure_directories()
    urls = read_urls(INPUT_FILE)

    if not urls:
        print("No URLs found to ingest.")
        return

    for url in urls:
        ingest_url(url)

    print("Ingestion complete.")


if __name__ == "__main__":
    main()
