# Setup

## Prerequisites

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/) is recommended, but any Python package manager will work

## Installing dependencies

With uv:

```
uv sync
```

With pip:

```
pip install -e .
```

## Running the script

With uv:

```
uv run python ./main.py
```

Or, with an active virtual environment:

```
python ./main.py
```

## Running the tests

With uv:

```
uv run pytest -v
```

Or, with an active virtual environment:

```
pytest -v
```
