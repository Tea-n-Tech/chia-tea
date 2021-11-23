import os
from typing import Optional

import typer

from ..utils.config import config_is_loaded, read_config
from .config import config_cmd
from .copy import copy_cmd

app = typer.Typer()
app.add_typer(config_cmd, name="config")
app.add_typer(copy_cmd, name="copy")

# @app.callback()
# def main(config: str = Optional[str]):
#     """
#     """

#     # Load config file
#     if config:
#         read_config(config)
#     else:
#         default_filepaths = ["config.yml", "~/.chia_tea/config.yml"]
#         for filepath in default_filepaths:
            
#             if filepath.startswith("~"):
#                 filepath = os.path.expanduser(filepath)
            
#             if os.path.isfile(filepath):
#                 read_config(filepath)

#     if not config_is_loaded():
#         typer.echo("No config file found. Please run `chia_tea init`.")

if __name__ == "__main__":
    app()
