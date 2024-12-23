from auto_review_tool.core.config import settings


def initialize_auto_review_tool() -> None:
    """
    Initializes settings by loading environment variables.
    """
    env_dict = settings.env_dict
    for key, value in env_dict.items():
        if value is None:
            raise ValueError(
                f"You need to set {key} in your environment variables."
            )


initialize_auto_review_tool()
