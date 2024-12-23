from typing import List, Literal

from pydantic import BaseModel, HttpUrl


class ReviewRequest(BaseModel):
    """
    A ReviewRequest model.
    """
    assignment_description: str
    github_repo_url: HttpUrl
    candidate_level: Literal["Junior", "Middle", "Senior"]


class ReviewResponse(BaseModel):
    found_files: List[str]
    analysis: str
