import csv
import json
import os
from typing import Any, Dict, Optional

import typer

app = typer.Typer()

TYPES_CONFIG = ("date", "filter", "combine", "new")


@app.callback()
def main(input: str, output: str, config: str, force: bool = False):
    if os.path.isfile(input):
        typer.echo(f"{input} file not found")
        raise typer.Exit()
    if os.path.dirname(os.path.abspath(output)):
        typer.echo(f"{output} directory not found")
        raise typer.Exit()
    if os.path.isfile(output) and not force:
        typer.echo(f"{output} file already exist. Use --force to overwrite")
        raise typer.Exit()
    if os.path.isfile(config):
        typer.echo(f"{config} file not found")
        raise typer.Exit()
    with open("names.csv") as csvfile:
        data = csv.DictReader(csvfile)
        f = open(
            "data.json",
        )
        CONFIG = json.load(f)
        if "type" not in CONFIG.keys():
            typer.echo("Type not found in provided config file!")
        _type = CONFIG["type"]
        check_supported_type(_type=_type)
        if _type == "new":
            resp = add_columns(file_data=data)
        if _type == "filter":
            resp = filter_by(file_data=data)
        if _type == "date":
            resp = date_format(file_data=data)
        if _type == "combine":
            resp = combine_columns(file_data=data)
        if not resp:
            typer.echo("Operation failed. Check input file or config.")
            raise typer.Exit()
        write_to_file(dict_to_write=resp, path_to_file=output)
    typer.echo(f"Data Generated successfully. View the file at {output}")


def check_supported_type(_type: str) -> None:
    if _type not in TYPES_CONFIG:
        typer.echo("Type not supported! Use types command to see available types")
        raise typer.Exit()


def write_to_file(dict_to_write: Dict[str, Any], path_to_file: str) -> bool:
    try:
        with open(path_to_file, "w") as f:
            w = csv.DictWriter(f, dict_to_write.keys())
            w.writeheader()
            w.writerow(dict_to_write)
        return True
    except:
        return False


@app.command()
def types(option: Optional[str] = None):
    if not option:
        typer.echo(f"Available types are {TYPES_CONFIG}")
        raise typer.Exit()
    check_supported_type(_type=option)
    if option == "date":
        typer.echo("Provide column name to format in 'column' key")
        typer.echo("Provide format in 'format' key")
        raise typer.Exit()
    if option == "filter":
        typer.echo("Provide column name to operate on 'column' key")
        typer.echo(
            "Provide operator in 'operator' key. Supported operators are > , <, >=,<=,=="
        )
        typer.echo("Provide value/operand to format in 'value' key")
        raise typer.Exit()

    if option == "combine":
        typer.echo("Provide first column name 'column1' key")
        typer.echo("Provide second column name 'column2' key")
        raise typer.Exit()
    if option == "new":
        typer.echo("Provide new column name 'column' key")
        typer.echo("Provide column name to operate on 'column1' key")
        typer.echo(
            "Provide operator in 'operator' key. Supported operators are > , <, >=,<=,==,+,-,*"
        )
        typer.echo("Provide value/operand to format in 'value' key")
        raise typer.Exit()


def date_format(file_data: Dict[str, Any]) -> Dict[str, Any]:
    return {"input": ""}


def filter_by(file_data: Dict[str, Any]) -> Dict[str, Any]:
    return {"input": ""}


def combine_columns(file_data: Dict[str, Any]) -> Dict[str, Any]:
    return {"input": ""}


def add_columns(file_data: Dict[str, Any]) -> Dict[str, Any]:
    return {"input": ""}


if __name__ == "__main__":
    app()
