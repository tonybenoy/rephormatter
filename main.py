#!/usr/bin/python3
import csv
import json
import os
from typing import Any, Dict, Optional

import pandas as pd
import typer

app = typer.Typer()


def date_format(file_data: pd.DataFrame, extra_info: Dict[str, Any]) -> pd.DataFrame:
    if not extra_info.get("column_to_format"):
        typer.echo("Please provide a column for formatting")
        raise typer.Exit()
    if not extra_info.get("format"):
        typer.echo("Please a valid format")
        raise typer.Exit()
    pd.to_datetime(file_data[extra_info["column_to_format"]]).dt.strftime(
        extra_info["format"]
    )
    return file_data


def filter_by(file_data: pd.DataFrame, extra_info: Dict[str, Any]) -> pd.DataFrame:
    if not extra_info.get("column"):
        typer.echo("Please provide a column for filtering")
        raise typer.Exit()
    if not extra_info.get("value"):
        typer.echo("Please provide a value for filtering")
        raise typer.Exit()
    OPS = ("==", "<", "<=", ">", ">=", "!=")
    if extra_info.get("operator") not in OPS:
        typer.echo("Unsupported Operator")
        raise typer.Exit()

    if extra_info.get("operator") == "!=":
        return file_data[
            file_data[extra_info["column"]] != extra_info["value"]
        ].to_frame()
    if extra_info.get("operator") == ">":
        return file_data[
            file_data[extra_info["column"]] > extra_info["value"]
        ].to_frame()
    if extra_info.get("operator") == ">=":
        return file_data[
            file_data[extra_info["column"]] >= extra_info["value"]
        ].to_frame()
    if extra_info.get("operator") == "==":
        return file_data[
            file_data[extra_info["column"]] == extra_info["value"]
        ].to_frame()
    if extra_info.get("operator") == "<":
        return file_data[
            file_data[extra_info["column"]] < extra_info["value"]
        ].to_frame()
    if extra_info.get("operator") == "<=":
        return file_data[
            file_data[extra_info["column"]] <= extra_info["value"]
        ].to_frame()
    return file_data


def combine_columns(
    file_data: pd.DataFrame, extra_info: Dict[str, Any]
) -> pd.DataFrame:
    if not extra_info.get("column1"):
        typer.echo("Please provide a column1 for combining")
        raise typer.Exit()
    if not extra_info.get("column2"):
        typer.echo("Please provide a column2 for combining")
        raise typer.Exit()
    if not extra_info.get("newcolumn"):
        typer.echo("Please provide a newcolumn for combining")
        raise typer.Exit()
    file_data[extra_info.get("newcolumn")] = file_data.apply(
        lambda x: "%s is %s"
        % (x[extra_info.get("column1")], x[extra_info.get("column2")]),
        axis=1,
    )
    return file_data


def add_columns(file_data: pd.DataFrame, extra_info: Dict[str, Any]) -> pd.DataFrame:
    OPS = (">", "<", ">=", "<=", "==", "+", "-", "*", "/")
    if not extra_info.get("column"):
        typer.echo("Please provide a column for filtering")
        raise typer.Exit()
    if not extra_info.get("value"):
        typer.echo("Please provide a value for filtering")
        raise typer.Exit()
    if not extra_info.get("newcolumn"):
        typer.echo("Please provide a newcolumn for combining")
        raise typer.Exit()
    OPS = ("==", "<", "<=", ">", ">=", "!=", "+", "-", "*", "/")
    if extra_info.get("operator") not in OPS:
        typer.echo("Unsupported Operator")
        raise typer.Exit()
    if extra_info["operator"] == "!=":
        file_data["newcolumn"] = file_data[extra_info["column"]] != extra_info["value"]
    if extra_info["operator"] == "==":
        file_data["newcolumn"] = file_data[extra_info["column"]] == extra_info["value"]
    if extra_info["operator"] == "<=":
        file_data["newcolumn"] = file_data[extra_info["column"]] <= extra_info["value"]
    if extra_info["operator"] == "<":
        file_data["newcolumn"] = file_data[extra_info["column"]] < extra_info["value"]
    if extra_info["operator"] == ">=":
        file_data["newcolumn"] = file_data[extra_info["column"]] >= extra_info["value"]
    if extra_info["operator"] == ">":
        file_data["newcolumn"] = file_data[extra_info["column"]] > extra_info["value"]
    if extra_info["operator"] == "+":
        file_data["newcolumn"] = file_data[extra_info["column"]] + extra_info["value"]
    if extra_info["operator"] == "*":
        file_data["newcolumn"] = file_data[extra_info["column"]] * extra_info["value"]
    if extra_info["operator"] == "-":
        file_data["newcolumn"] = file_data[extra_info["column"]] - extra_info["value"]
    if extra_info["operator"] == "/":
        file_data["newcolumn"] = file_data[extra_info["column"]] / extra_info["value"]
    return file_data


TYPE_METHOD_DICT = {
    "date": date_format,
    "filter": filter_by,
    "combine": combine_columns,
    "new": add_columns,
}


@app.command()
def run(input: str, output: str, config: str, force: bool = False):
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
    data = pd.read_csv(input)
    f = open(config)
    CONFIG = json.load(f)
    if "type" not in CONFIG.keys():
        typer.echo("Type not found in provided config file!")
    _type = CONFIG["type"]
    check_supported_type(_type=_type)
    resp = TYPE_METHOD_DICT[_type](file_data=data)
    if not resp:
        typer.echo("Operation failed. Check input file or config.")
        raise typer.Exit()
    if write_to_file(dict_to_write=resp, path_to_file=output):
        typer.echo(f"Data Generated successfully. View the file at {output}")
        raise typer.Exit()
    typer.echo(f"Unable to save as {output}")


def check_supported_type(_type: str) -> None:
    if _type not in TYPE_METHOD_DICT.keys():
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
        typer.echo(f"Available types are {set(TYPE_METHOD_DICT.keys())}")
        raise typer.Exit()
    check_supported_type(_type=option)
    if option == "date":
        typer.echo("Provide column name to format in 'column' key")
        typer.echo("Provide format in 'format' key")
        typer.echo("%a - abbreviated weekday name")
        typer.echo("%A - full weekday name")
        typer.echo("%b - abbreviated month name")
        typer.echo("%B - full month name")
        typer.echo("%d - day of the month (01 to 31)")
        typer.echo("%D - same as %m/%d/%y")
        typer.echo("%m - month (01 to 12)")
        typer.echo(
            "%u - weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1"
        )
        typer.echo("%w - day of the week as a decimal, Sunday=0")
        typer.echo("%y - year without a century (range 00 to 99)")
        typer.echo("%Y - year including the century")
        raise typer.Exit()
    if option == "filter":
        typer.echo("Provide column name to operate on 'column' key")
        typer.echo(
            "Provide operator in 'operator' key. Supported operators are > , <, >=,<=,==,!="
        )
        typer.echo("Provide value/operand to format in 'value' key")
        raise typer.Exit()

    if option == "combine":
        typer.echo("Provide first column name 'column1' key")
        typer.echo("Provide second column name 'column2' key")
        typer.echo("Provide new column name 'newcolumn' key")
        raise typer.Exit()
    if option == "new":
        typer.echo("Provide new column name 'column' key")
        typer.echo("Provide column name to operate on 'newcolumn' key")
        typer.echo(
            "Provide operator in 'operator' key. Supported operators are > , <, >=,<=,==,+,-,*"
        )
        typer.echo("Provide value/operand to format in 'value' key")
        raise typer.Exit()


if __name__ == "__main__":
    app()
