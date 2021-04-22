from typer.testing import CliRunner

from main import app

runner = CliRunner()


def test_app():
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage: root [OPTIONS] COMMAND [ARGS]" in result.stdout


def test_app2():
    result = runner.invoke(app, ["types"])
    assert result.exit_code == 0
    assert "filter" in result.stdout
