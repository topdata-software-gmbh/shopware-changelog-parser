from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

class ChangelogEntry(BaseModel):
    """Represents a single changelog entry."""
    date: str # when using date it failed with string 2020-25-10
    title: str
    version: str
    file: str
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
