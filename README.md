# calculators

A dashboard of physics calculators

## Requirements

- Python 3.6+
- [poetry](https://python-poetry.org/)

## Makefile targets

- `prepare`: install the required dependencies using poetry. On Windows, run `poetry install`.
- `run`: run the plugin. On Windows, `poetry run python calculators`.
- `clean`: removes poetry lockfile and virtual environment.
- `services` (Unix only): create and install a unit service file to run the plugin server via `systemctl`.
