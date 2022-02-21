import os
from asyncio import Lock
from datetime import datetime, timedelta
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

load_dotenv(".env.test")

app = FastAPI()

# test comment
class Counter:
    def __init__(self):
        self.val = 10
        self.lock = Lock()

    async def get_and_increment(self) -> int:
        async with self.lock:
            val = self.val
            self.val += 1
            return val


counter = Counter()
db = {}


class ExtractSpec(BaseModel):
    description: str
    data_format: str
    data_structure: Dict[str, dict]
    samples: Dict[str, dict]
    variables: Dict[str, dict]


@app.post("/extracts")
async def submit_extract(
    collection: str,
    extract: ExtractSpec,
    request: Request,
    version: str = "v1",
):
    if request.headers["Authorization"] != os.environ.get("IPUMS_API_KEY"):
        raise HTTPException(403, "Incorrect api key")

    number = await counter.get_and_increment()
    db[number] = datetime.utcnow()
    return {"number": number}


@app.get("/extracts/{extract_id}")
async def download_extract(extract_id: int, request: Request):
    if request.headers["Authorization"] != os.environ.get("IPUMS_API_KEY"):
        raise HTTPException(403, "Incorrect api key")

    if extract_id in db:
        if datetime.utcnow() - db[extract_id] > timedelta(seconds=3):
            return {
                "status": "completed",
            }
        else:
            return {"status": "started"}
    raise HTTPException(404, "Not found")


@app.get("/extracts")
async def retrieve_previous_extracts(
    collection: str,
    request: Request,
    limit: int = 10,
    version: str = "v1",
):
    if request.headers["Authorization"] != os.environ.get("IPUMS_API_KEY"):
        raise HTTPException(403, "Incorrect api key")

    return {collection: list(range(10))}
