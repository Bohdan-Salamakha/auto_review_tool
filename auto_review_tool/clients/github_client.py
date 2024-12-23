import base64
import logging
from hashlib import sha256
from typing import Any, Dict, List, Optional

from httpx import AsyncClient, HTTPStatusError

from auto_review_tool.core.redis_client import redis_client


class GitHubClient:
    def __init__(self, token: str) -> None:
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def get_repo_contents(self, repo_url: str) -> List[Dict[str, Any]]:
        """
        Get the contents of the repository.
        :param repo_url: URL of the repository (e.g., https://github.com/user/repo)
        :return: List of files and folders in the repository.
        """
        logging.info('Getting repo contents...')
        cache_key = f"repo_contents:{repo_url}"
        cached_data = await self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data

        api_url = self._construct_repo_api_url(repo_url)
        response_data = await self._fetch_data_from_api(api_url)

        file_list_tree = response_data.get("tree", [])
        files = [item for item in file_list_tree if item["type"] == "blob"]

        await self._cache_data(cache_key, files)
        return files

    async def get_file_contents(self, files: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Get the contents of all files in the repository.
        :param files: List of files (result of get_repo_contents).
        :return: Dictionary with file paths and their contents.
        """
        logging.info('Getting file contents...')
        contents = {}
        async with AsyncClient() as client:
            for file_details_dict in files:
                file_url = file_details_dict["url"]
                cache_key = (
                    f"file_content:"
                    f"{sha256(file_url.encode('utf-8')).hexdigest()}"
                )

                cached_content = await self._get_cached_data(cache_key)
                if cached_content is not None:
                    contents[file_details_dict["path"]] = cached_content
                    continue

                content = await self._fetch_file_content(client, file_url)
                if content is not None:
                    decoded_content = base64.b64decode(content).decode("utf-8")
                else:
                    decoded_content = ""

                contents[file_details_dict["path"]] = decoded_content
                await self._cache_data(cache_key, decoded_content)

        return contents

    async def is_api_available(self) -> bool:
        api_url = f"{self.base_url}/rate_limit"
        response_data = await self._fetch_data_from_api(api_url)
        remaining_api_usage = response_data.get("rate", {}).get("remaining", 0)
        return remaining_api_usage > 0

    @staticmethod
    async def _get_cached_data(cache_key: str) -> Optional[Any]:
        """Retrieve data from cache."""
        if redis_client.is_connected:
            cached_data = await redis_client.get(cache_key)
            if cached_data is not None:
                logging.info(f"Found cached data for {cache_key}")
                return cached_data
        return None

    @staticmethod
    async def _cache_data(cache_key: str, data: Any, expire: int = 3600) -> None:
        """Cache data in Redis."""
        if redis_client.is_connected:
            await redis_client.set(cache_key, data, expire=expire)
            logging.info(f"Cached data for {cache_key}")

    def _construct_repo_api_url(self, repo_url: str) -> str:
        """Construct the API URL for a repository."""
        parts = repo_url.rstrip("/").split("/")
        try:
            repo = parts.pop()
            owner = parts.pop()
        except IndexError:
            raise ValueError(f"Invalid repository URL: {repo_url}")
        return f"{self.base_url}/repos/{owner}/{repo}/git/trees/master?recursive=1"

    async def _fetch_data_from_api(self, url: str) -> dict:
        """Fetch data from the GitHub API."""
        async with AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except HTTPStatusError as e:
                raise ValueError(
                    f"Error while requesting GitHub API: "
                    f"{e.response.status_code}, {e.response.text}"
                )

    async def _fetch_file_content(
            self,
            client: AsyncClient,
            file_url: str
    ) -> Optional[str]:
        """Fetch the content of a single file from GitHub."""
        try:
            response = await client.get(file_url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("content")
        except Exception as e:
            logging.error(f"Failed to get file content from {file_url}: {e}")
            return None
