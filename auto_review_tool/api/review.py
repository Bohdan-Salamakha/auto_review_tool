from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from auto_review_tool.clients.github_client import GitHubClient
from auto_review_tool.clients.openai_client import OpenAIClient
from auto_review_tool.core.config import settings
from auto_review_tool.models.review import ReviewRequest, ReviewResponse

router = APIRouter()
github_client = GitHubClient(token=settings.GITHUB_TOKEN)
openai_client = OpenAIClient(api_key=settings.OPENAI_API_KEY)


@router.post("/review", response_model=ReviewResponse)
async def review_code(request: ReviewRequest) -> ReviewResponse:
    """
    Endpoint for automated code review.
    """
    try:
        if not await github_client.is_api_available():
            raise HTTPException(
                status_code=503,
                detail=(
                    "The service is temporarily unavailable "
                    "due to internal API rate limits. "
                    "Please try again later."
                ),
                headers={"Retry-After": settings.RETRY_AFTER},
            )
        repo_contents: List[Dict[str, Any]] = await github_client.get_repo_contents(
            str(request.github_repo_url)
        )
        all_file_names = [item["path"] for item in repo_contents]
        file_contents = await github_client.get_file_contents(repo_contents)
        analysis = await openai_client.analyze_code(
            file_names=list(file_contents.keys()),
            file_contents=list(file_contents.values()),
            assignment_description=request.assignment_description,
            candidate_level=request.candidate_level,
        )
        return ReviewResponse(
            found_files=all_file_names,
            analysis=analysis
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
