
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from typing import Optional, Dict, Any
from datetime import datetime

class StringItem(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    value: str = Field(index=True)
    properties: Dict[str, Any] = Field(sa_column=Column(JSON))  # ✅ removed nullable
    created_at: datetime
