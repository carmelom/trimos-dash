# Mode solver Dashboard

A dashboard to visualize normal modes of trapped ions - powered by [TRIMOS](https://github.com/carmelom/trimos) and [slapdash](https://github.com/cathaychris/slapdash)

## Installation

    poetry install

## Usage

    poetry run mode_solver_dashboard

## Authors and acknowledgment

- Carmelo Mordini & the TIQI group

## License

MIT

## Makefile targets

- `install`: install the required dependencies using poetry. On Windows, run `poetry install`.
- `run`: run the dashboard. On Windows, `poetry run python mode_solver_dashboard`.
- `clean`: removes poetry lockfile and virtual environment.
- `services` (Unix only): create and install a unit service file to run the dashboard server via `systemctl`.
