# Trimos-dash

A dashboard to visualize normal modes of trapped ions - powered by [trimos](https://github.com/carmelom/trimos) and [slapdash](https://github.com/cathaychris/slapdash)

## Installation

    poetry install

## Usage

    poetry run trimos_dash

## Authors and acknowledgment

- Carmelo Mordini & the TIQI group

## License

MIT

## Makefile targets

- `install`: install the required dependencies using poetry. On Windows, run `poetry install`.
- `run`: run the dashboard. On Windows, `poetry run python trimos_dash`.
- `clean`: removes poetry lockfile and virtual environment.
- `services` (Unix only): create and install a unit service file to run the dashboard server via `systemctl`.
