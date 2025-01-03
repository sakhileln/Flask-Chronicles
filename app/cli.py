"""
This module provides command-line interface (CLI) commands for managing 
translations and localization within the application.

Commands:
- translate: A CLI group for translation and localization commands.
    - init: Initialize a new language by extracting messages and creating 
      translation files.
    - update: Update existing translation files for all languages based on 
      the current source code.
    - compile: Compile the translation files into binary format for use in 
      the application.

- Babel: Used for extracting, initializing, updating, and compiling 
  translations.

Usage:
To use these commands, run the following in the terminal:
$ flask translate <command>
"""

import os
from flask import Blueprint
import click

bp = Blueprint("cli", __name__, cli_group=None)


@bp.cli.group()
def translate():
    """Translation and localization commands."""


@translate.command()
@click.argument("lang")
def init(lang):
    """Initialize a new language."""
    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError("extract command failed")
    if os.system("pybabel init -i messages.pot -d app/translations -l " + lang):
        raise RuntimeError("init command failed")
    os.remove("messages.pot")


@translate.command()
def update():
    """Update all languages."""
    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError("extract command failed")
    if os.system("pybabel update -i messages.pot -d app/translations"):
        raise RuntimeError("update command failed")
    os.remove("messages.pot")


# pylint: disable=redefined-builtin
@translate.command()
def compile():
    """Compile all languages."""
    if os.system("pybabel compile -d app/translations"):
        raise RuntimeError("compile command failed")
