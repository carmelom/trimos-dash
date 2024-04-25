# Trimos-dash

A dashboard to visualize normal modes of trapped ions - powered by [trimos](https://github.com/carmelom/trimos) and [slapdash](https://github.com/cathaychris/slapdash)

## Requirements

- python >=3.9, <3.12
- [poetry](https://python-poetry.org/)

## Installation

    poetry install

## Usage

    poetry run trimos_dash [--port PORT]

Run the command, optionally specifying the port number for the web application (default: 8050). Then browse to <http://localhost:8050>

## Authors and acknowledgment

- Carmelo Mordini & the TIQI group at ETH Zurich

## License

MIT

## Makefile targets

Mostly Linux-oriented, although make exists on Windows too.

- `install`: install the project and the required dependencies using poetry.
- `run`: run the dashboard.
- `clean`: removes poetry lockfile and virtual environment.
- `nohup_run`: run the dashboard in background via `nohup`.
- `nouhp_kill`: kills the background process.
