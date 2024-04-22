import os
import typer
import uvicorn

from pathlib import Path
from rich.console import Console
from rich.markup import escape

from toolserve.common.log import log
from toolserve.server.core.conf import settings
from toolserve.server.main import app
from toolserve.apm.pack import Packer


cli = typer.Typer()
console = Console()

@cli.command(help="Starts the ToolServer with specified configurations.")
def serve(
    host: str = typer.Option(
        settings.UVICORN_HOST,
        help="Host for the app, from settings by default.",
        show_default=True
    ),
    port: int = typer.Option(
        settings.UVICORN_PORT,
        help="Port for the app, settings default.",
        show_default=True
    ),
):
    """
    Starts the server with host, port, and reload options. Uses
    Uvicorn as ASGI server. Parameters allow runtime configuration.
    """
    try:
        uvicorn.run(
            app=app,
            host=host,
            port=port,
        )
    except KeyboardInterrupt:
        console.print("Server stopped by user.", style="bold red")
        typer.Exit()
    except Exception as e:
        error_message = f'❌ Failed to start Toolserver: {escape(str(e))}'
        console.print(error_message, style="bold red")
        raise typer.Exit(code=1)

@cli.command(help="Build a new Tool Pack")
def pack(
    directory: str = typer.Option(
        os.getcwd(),
        "--dir",
        help="tools directory path with pack.toml"
    ),
):
    """
    Creates a new tool pack with the given name, description, and result type.
    """
    try:
        pack = Packer(directory)
        pack.create_pack()
    except Exception as e:
        error_message = f'❌ Failed to build Tool Pack: {escape(str(e))}'
        console.print(error_message, style="bold red")
        raise typer.Exit(code=1)