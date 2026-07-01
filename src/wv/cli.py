"""Typer command-line interface for Weather Vision.

This module defines the ``analyze`` command (invoked via ``wv <path>``)
that validates the input and prints the structured result as JSON.
"""

from pathlib import Path

import typer
from httpx import HTTPError
from pydantic import ValidationError
from pydantic_ai import ModelRetry
from rich.console import Console
from rich.json import JSON

from wv.agent import analyze_image
from wv.exceptions import InvalidImageError

console = Console()

app = typer.Typer(
    name="wv",
    help="Weather image analysis via PydanticAI + OpenRouter.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def analyze(
    path: Path = typer.Argument(
        ..., exists=False, readable=True, help="Path to the image file"
    ),
) -> None:
    """Analyze a weather image and print the result as JSON.

    Raises
    ------
    typer.Exit
        With code 2 for input errors or 1 for runtime/model errors.
    """
    try:
        result = analyze_image(path)
    except FileNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from None
    except InvalidImageError as exc:
        typer.echo(f"Invalid image: {exc}", err=True)
        raise typer.Exit(code=2) from None
    except OSError as exc:
        typer.echo(f"Error reading file '{path}': {exc}", err=True)
        raise typer.Exit(code=2) from None
    except ValidationError as exc:
        typer.echo(f"Model schema error: {exc}", err=True)
        raise typer.Exit(code=1) from None
    except ModelRetry as exc:
        typer.echo(
            f"Model failed to produce valid output after retries: {exc}",
            err=True,
        )
        raise typer.Exit(code=1) from None
    except HTTPError as exc:
        typer.echo(f"OpenRouter communication error: {exc}", err=True)
        raise typer.Exit(code=1) from None
    except Exception as exc:
        typer.echo(f"Unexpected failure: {exc}", err=True)
        raise typer.Exit(code=1) from None

    console.print(JSON(result.model_dump_json()))
