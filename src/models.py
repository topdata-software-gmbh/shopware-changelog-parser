from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

class ChangelogEntry(BaseModel):
    """Represents a single changelog entry."""
    date: date
    title: str
    version: str
    content: str = Field(default="")
    issue: Optional[str] = None
    author: Optional[str] = None
    author_email: Optional[str] = None
    author_github: Optional[str] = None

class VersionComparison(BaseModel):
    """Represents a comparison between two versions."""
    from_version: str
    to_version: str
    entries: list[ChangelogEntry]
