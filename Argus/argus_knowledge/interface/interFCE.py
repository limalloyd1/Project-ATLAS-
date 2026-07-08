import os
import math 
import random
import json
from pathlib import Path

PROCESSED_DIR = Path("/home/limalima/AtlasProj/Argus/data/processed/learnopengl/documents")

def load_documents() -> list:
    # traverse through directory to take text from .json files -> append to list 
    docs = []
    for item in PROCESSED_DIR.glob("*.json"):
        try:
            with open(item, 'r', encoding="utf-8") as infile:
                data = json.load(infile)
            
            title = data.get("title","")
            text = data.get("text", "").strip()
            url = data.get("url", "")
            doc_id = data.get("document_id","")
            # docs.append({"title": title, "text": text, "url": url})
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

        if not text:
            continue
        
        docs.append({
            "document_id": doc_id,
            "title": title,
            "text": text,
            "url": url
        })
    
    if docs == []:
        print("No data appended")
        return []
    else:
        print("Docs succesfully loaded")
        return docs

def chunkData(docs: list) -> list: # output to json eventually
    results = [] 
    for doc in docs:
        text = doc["text"]
        paragraphs = text.split("\n\n") # end of paragraph flag

        chunk = ""
        chunk_index = 0

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue

            # keep size limit -> 800
            if len(chunk) + len(p) < 800:
                chunk +=" " + p
            else:
                # save chunk 
                results.append({
                    "chunk_id": f"{doc['document_id']}_{chunk_index}",
                    "document_id": doc["document_id"],
                    "title": doc["title"],
                    "url": doc["url"],
                    "chunk_index": chunk_index,
                    "text": chunk.strip()
                    })


                chunk_index += 1
                chunk = p
            
        # save leftover chunk
        if chunk:
            results.append({
                "chunk_id": f"{doc['document_id']}_{chunk_index}",
                "document_id": doc["document_id"],
                "title": doc["title"],
                "url": doc["url"],
                "chunk_index": chunk_index,
                "text": chunk.strip()
            })

    return results 



def main():
    d = load_documents()    

    print(f"Loaded {len(d)} documents")

    print(d[0])
    print(d[0].keys())
    # print(d[1]["text"])
    # print(d[1]["url"])

    print("CHUNKING DATA...")
    print()
    r = chunkData(d)
    print(f"{len(r)} items processed")

if __name__ == "__main__":
    main()


