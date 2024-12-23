import logging
from collections.abc import Buffer
from hashlib import sha256
from typing import List

from openai import OpenAI

from auto_review_tool.core.redis_client import redis_client


class OpenAIClient:
    def __init__(self, api_key: str) -> None:
        """
        Initializing the OpenAI client.
        :param api_key: OpenAI API key.
        """
        self.client = OpenAI(api_key=api_key)

    @staticmethod
    def __get_formatted_prompt(
            file_names: list[str],
            file_contents: list[str],
            assignment_description: str,
            candidate_level: str
    ) -> str:
        prompt = f"""You are a coding reviewer for {candidate_level}-level developers.
Please review the following coding assignment:
Assignment Description:

{assignment_description}

Analyze the code files and provide feedback on the following:
- Code quality
- Possible improvements
- Any bugs or issues

Here are the contents of the files:
"""
        files_content = "".join(
            [
                f"File: {name}\nContent: {content}\n\n"
                for name, content in zip(file_names, file_contents)
            ]
        )
        prompt += files_content
        prompt += """Please summarize your analysis in the following format:
- Downsides/Comments:
- Rating (1 to 5):
- Conclusion:"""
        return prompt

    async def analyze_code(
            self,
            file_names: List[str],
            file_contents: List[str],
            assignment_description: str,
            candidate_level: str
    ) -> str:
        """
        Analyzes code using the OpenAI API.
        :param file_names: List of file names.
        :param file_contents: List of file contents.
        :param assignment_description: Description of the assignment.
        :param candidate_level: Candidate level (Junior, Middle, Senior).
        :return: Analysis result.
        """
        logging.info('Analyzing code...')
        cache_string: str = (
                ''.join(file_names) + ''.join(file_contents) +
                assignment_description + candidate_level
        )
        cache_string_encoded: Buffer = cache_string.encode('utf-8')
        cache_key = (
            f"code_analysis:"
            f"{sha256(cache_string_encoded).hexdigest()}"
        )
        if redis_client.is_connected:
            cached_analysis = await redis_client.get(cache_key)
            if cached_analysis:
                logging.info('Found cached data for "analyze_code"')
                return cached_analysis

        prompt = self.__get_formatted_prompt(
            file_names,
            file_contents,
            assignment_description,
            candidate_level,
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a coding reviewer."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.5
            )
            analysis = response.choices[0].message.content

            if redis_client.is_connected:
                logging.info('Caching data for "analyze_code"')
                await redis_client.set(cache_key, analysis, expire=86400)
            return analysis
        except Exception as e:
            raise ValueError(f"Error while requesting OpenAI API: {str(e)}")
