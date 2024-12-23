import logging

import click
import uvicorn

from auto_review_tool.main import app


@click.group()
def cli() -> None:
    """Auto Review Tool CLI"""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to run the server")
@click.option("--port", default=8000, type=int, help="Port to run the server")
@click.option("--workers", default=4, type=int, help="Number of workers")
@click.option("--reload", is_flag=True, help="Enable auto-restart for development")
def runprod(host: str, port: int, workers: int, reload: bool) -> None:
    """
    Runs the server in Production mode with Uvicorn.
    """
    if reload:
        logging.warning(
            "You started the server with the --reload option. "
            "This is not recommended for Production."
        )
    logging.info(f"Launching the server on {host}:{port} with {workers} workers.")
    uvicorn.run(
        "auto_review_tool.main:app",
        host=host,
        port=port,
        workers=workers,
        reload=reload,
    )


@cli.command()
def rundev() -> None:
    """Starts the FastAPI server"""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    cli()
