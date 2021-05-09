import os
from typing import Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

load_dotenv(".env.test")

app = FastAPI()


class ExtractSpec(BaseModel):
    description: str
    data_format: str
    data_structure: Dict[str, dict]
    samples: Dict[str, dict]
    variables: Dict[str, dict]


@app.post("/extracts")
async def submit_extract(
    collection: str, extract: ExtractSpec, request: Request, version: str = "v1",
):
    if request.headers["Authorization"] != os.environ.get("IPUMS_API_KEY"):
        raise HTTPException(403, "Incorrect api key")
    return {"number": 10}


@app.get("/extracts")
async def retrieve_previous_extracts(
    collection: str, request: Request, limit: int = 10, version: str = "v1",
):
    if request.headers["Authorization"] != os.environ.get("IPUMS_API_KEY"):
        raise HTTPException(403, "Incorrect api key")

    return {collection: list(range(10))}
