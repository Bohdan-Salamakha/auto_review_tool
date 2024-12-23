from unittest.mock import AsyncMock

import pytest

from auto_review_tool.clients.openai_client import OpenAIClient


@pytest.mark.asyncio
async def test_analyze_code():
    client = OpenAIClient(api_key="test_key")
    mock_analysis = "Downsides: None. Rating: 5. Conclusion: Excellent code."

    client.analyze_code = AsyncMock(return_value=mock_analysis)

    result = await client.analyze_code(
        ["file1.py"],
        ["print('hello world')"],
        "Analyze a simple Python file.",
        "Junior"
    )

    assert "Downsides" in result
    assert "Rating" in result
