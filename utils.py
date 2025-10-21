import hashlib
import collections
from pydantic import BaseModel

class Properties(BaseModel):
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: dict

def compute_properties(value: str) -> Properties:
    s = value
    length = len(s)
    is_palindrome = s.lower() == s.lower()[::-1]
    unique_characters = len(set(s))
    word_count = len(s.split())
    sha = hashlib.sha256(s.encode("utf-8")).hexdigest()
    freq = dict(collections.Counter(list(s)))
    return Properties(
        length=length,
        is_palindrome=is_palindrome,
        unique_characters=unique_characters,
        word_count=word_count,
        sha256_hash=sha,
        character_frequency_map=freq,
    )

def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
