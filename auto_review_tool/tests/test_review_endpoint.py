from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from auto_review_tool.clients.github_client import GitHubClient
from auto_review_tool.clients.openai_client import OpenAIClient
from auto_review_tool.main import app


@pytest.mark.asyncio
@patch.object(GitHubClient, "get_repo_contents", new_callable=AsyncMock)
@patch.object(GitHubClient, "get_file_contents", new_callable=AsyncMock)
@patch.object(OpenAIClient, "analyze_code", new_callable=AsyncMock)
async def test_review_endpoint(
        mock_analyze_code,
        mock_get_file_contents,
        mock_get_repo_contents
):
    mock_get_repo_contents.return_value = [
        {"path": "file1.py", "type": "blob"},
        {"path": "file2.py", "type": "blob"}
    ]
    mock_get_file_contents.return_value = {
        "file1.py": "print('Hello, world!')",
        "file2.py": "def add(a, b): return a + b"
    }

    mock_analyze_code.return_value = (
        "- Downsides/Comments: None\n"
        "- Rating: 5\n"
        "- Conclusion: Excellent code"
    )

    with TestClient(app) as client:
        payload = {
            "assignment_description": "Review this code.",
            "github_repo_url": "https://github.com/test/repo",
            "candidate_level": "Junior"
        }
        response = client.post("/api/review", json=payload)

        assert response.status_code == 200

        json_response = response.json()
        assert "found_files" in json_response
        assert "analysis" in json_response

        assert json_response["found_files"] == ["file1.py", "file2.py"]
        assert "Excellent code" in json_response["analysis"]

    mock_get_repo_contents.assert_called_once_with("https://github.com/test/repo")
    mock_get_file_contents.assert_called_once()
    mock_analyze_code.assert_called_once()