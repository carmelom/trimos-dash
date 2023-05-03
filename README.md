# Mode solver Dashboard

A dashboard to visualize normal modes of trapped ions - powered by TRIMOS[^1]

## Requirements

- Python 3.6+
- [poetry](https://python-poetry.org/)

## Installation

    poetry install

## Usage

    poetry run mode_solver_dashboard

## Makefile targets

- `prepare`: install the required dependencies using poetry. On Windows, run `poetry install`.
- `run`: run the plugin. On Windows, `poetry run python calculators`.
- `clean`: removes poetry lockfile and virtual environment.
- `services` (Unix only): create and install a unit service file to run the plugin server via `systemctl`.

## Contributing

[...]

## Authors and acknowledgment

- Carmelo Mordini & the TIQI group

## License

MIT

[^1]: ThRee dImensional MOde Solver for trapped ions
