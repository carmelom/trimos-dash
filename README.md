# Physdash

A dashboard of physics calculators

## List of calculators

Current and future:

- [ ] Modes of an ion chain
- [ ] Rabi couplings
- [ ] Stark shifts and optical potentials
- [ ] ...

## Requirements

- Python 3.6+
- [poetry](https://python-poetry.org/)

## Installation

    poetry install

## Usage

[...]

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
