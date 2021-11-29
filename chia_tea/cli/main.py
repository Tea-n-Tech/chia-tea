import typer

from .config import config_cmd
from .start import start_cmd

app = typer.Typer(no_args_is_help=True)
app.add_typer(config_cmd, name="config")
app.add_typer(start_cmd, name="start")

if __name__ == "__main__":
    app()
