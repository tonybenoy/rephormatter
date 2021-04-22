from typer.testing import CliRunner

from main import app, combine_columns
import pandas as pd

runner = CliRunner()


def test_app():
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage: root [OPTIONS] COMMAND [ARGS]" in result.stdout


def test_app2():
    result = runner.invoke(app, ["types"])
    assert result.exit_code == 0
    assert "filter" in result.stdout


def test_combine_columns():
    fd = pd.DataFrame(
        [
            {"first_name": "Sachin", "last_name": "Tendulkar"},
            {"first_name": "Rahul", "last_name": "Dravid"},
            {"first_name": "Ricky", "last_name": "Ponting"},
        ]
    )
    resp = combine_columns(
        fd, {"column1": "first_name", "column2": "last_name", "newcolumn": "new"}
    )

    assert resp["new"].tolist() == ["Sachin Tendulkar", "Rahul Dravid", "Ricky Ponting"]
