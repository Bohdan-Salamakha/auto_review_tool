from unittest.mock import AsyncMock, patch

import pytest

from auto_review_tool.clients.github_client import GitHubClient
from auto_review_tool.core.redis_client import redis_client


@pytest.mark.asyncio
async def test_get_file_contents():
    client = GitHubClient(token="test_token")
    mock_files = [
        {"url": "https://api.github.com/file1", "path": "file1.py"},
        {"url": "https://api.github.com/file2", "path": "file2.py"},
    ]

    client.get_file_contents = AsyncMock(return_value={"file1.py": "print('hello world')"})

    contents = await client.get_file_contents(mock_files)
    assert "file1.py" in contents
    assert contents["file1.py"] == "print('hello world')"


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
@patch.object(redis_client, "get", new_callable=AsyncMock)
@patch.object(redis_client, "set", new_callable=AsyncMock)
async def test_get_repo_contents(mock_redis_get, _mock_redis_set, mock_httpx_get):
    mock_redis_get.return_value = None

    mock_httpx_get.return_value.status_code = 200
    mock_httpx_get.return_value.raise_for_status = AsyncMock
    mock_httpx_get.return_value.json = lambda: {
        "tree": [
            {"path": "file1.py", "type": "blob"},
            {"path": "file2.py", "type": "blob"},
            {"path": "folder/", "type": "tree"},
        ]
    }

    client = GitHubClient(token="mock_token")
    repo_url = "https://github.com/user/repo"

    result = await client.get_repo_contents(repo_url)

    assert len(result) == 2
    assert result[0]["path"] == "file1.py"
    assert result[1]["path"] == "file2.py"
