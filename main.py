from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select
from datetime import datetime, timezone
from typing import Optional, Any, Dict
import re

from database import engine
from models import StringItem, SQLModel
from utils import compute_properties, hash_value

app = FastAPI(title="String Analyzer Service")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/strings", status_code=201)
def create_string(data: Dict[str, Any]):
    if "value" not in data:
        raise HTTPException(status_code=400, detail='"value" field is required')
    if not isinstance(data["value"], str):
        raise HTTPException(status_code=422, detail='"value" must be a string')

    props = compute_properties(data["value"])
    with Session(engine) as session:
        if session.get(StringItem, props.sha256_hash):
            raise HTTPException(status_code=409, detail="String already exists")

        item = StringItem(
            id=props.sha256_hash,
            value=data["value"],
            properties=jsonable_encoder(props.dict()),
            created_at=datetime.now(timezone.utc),
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return jsonable_encoder(item)

@app.get("/strings/{string_value}")
def get_string(string_value: str):
    sha = hash_value(string_value)
    with Session(engine) as session:
        item = session.get(StringItem, sha)
        if not item:
            raise HTTPException(status_code=404, detail="String not found")
        return jsonable_encoder(item)

@app.get("/strings")
def get_all_strings(
    is_palindrome: Optional[bool] = Query(None),
    min_length: Optional[int] = Query(None),
    max_length: Optional[int] = Query(None),
    word_count: Optional[int] = Query(None),
    contains_character: Optional[str] = Query(None, min_length=1, max_length=1),
):
    with Session(engine) as session:
        items = session.exec(select(StringItem)).all()

    filtered = []
    for item in items:
        p = item.properties
        ok = True
        if is_palindrome is not None and p["is_palindrome"] != is_palindrome: ok = False
        if min_length is not None and p["length"] < min_length: ok = False
        if max_length is not None and p["length"] > max_length: ok = False
        if word_count is not None and p["word_count"] != word_count: ok = False
        if contains_character is not None and contains_character not in item.value: ok = False
        if ok: filtered.append(jsonable_encoder(item))

    return {
        "data": filtered,
        "count": len(filtered),
        "filters_applied": {
            k: v for k, v in {
                "is_palindrome": is_palindrome,
                "min_length": min_length,
                "max_length": max_length,
                "word_count": word_count,
                "contains_character": contains_character,
            }.items() if v is not None
        },
    }

def parse_natural_query(query: str) -> Dict[str, Any]:
    q = query.lower()
    parsed = {}
    if "palindrom" in q: parsed["is_palindrome"] = True
    if "single word" in q or "one word" in q: parsed["word_count"] = 1
    m = re.search(r"longer than (\d+)", q)
    if m: parsed["min_length"] = int(m.group(1)) + 1
    if "first vowel" in q: parsed["contains_character"] = "a"
    m2 = re.search(r"containing (?:the )?letter\s+([a-z])", q)
    if m2: parsed["contains_character"] = m2.group(1)
    return parsed

@app.get("/strings/filter-by-natural-language")
def natural_filter(query: str):
    parsed = parse_natural_query(query)
    if not parsed:
        raise HTTPException(status_code=400, detail="Unable to parse natural language query")

    resp = get_all_strings(**parsed)
    return {
        "data": resp["data"],
        "count": resp["count"],
        "interpreted_query": {"original": query, "parsed_filters": parsed},
    }

@app.delete("/strings/{string_value}", status_code=204)
def delete_string(string_value: str):
    sha = hash_value(string_value)
    with Session(engine) as session:
        item = session.get(StringItem, sha)
        if not item:
            raise HTTPException(status_code=404, detail="String not found")
        session.delete(item)
        session.commit()
    return JSONResponse(status_code=204, content=None)
