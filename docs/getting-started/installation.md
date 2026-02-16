# Installation

## Prerequisites

- **Python 3.11+**
- **PDM** (Python package manager)
- **Claude Code CLI** (for production workflows - optional for testing)

## Install PDM

If you don't have PDM installed:

```bash
curl -sSL https://pdm-project.org/install-pdm.py | python3 -
```

Or using pip:

```bash
pip install --user pdm
```

## Clone Repository

```bash
git clone https://github.com/ben/automated-software-pipeline-demo.git
cd automated-software-pipeline-demo
```

## Install Dependencies

```bash
pdm install
```

This installs all runtime dependencies defined in `pyproject.toml`.

## Install Development Dependencies

For testing and contributing:

```bash
pdm install -G dev
```

## Install Documentation Dependencies

To build docs locally:

```bash
pdm install -G docs
```

## Verify Installation

Run the test suite:

```bash
pdm run pytest tests/ -v
```

You should see all 33 tests passing.

## Optional: Install Claude Code CLI

For production workflows (not needed for mock testing):

Follow the [Claude Code installation guide](https://claude.com/claude-code).

## Next Steps

- [Quick Start](quick-start.md) - Run your first workflow
- [Testing](../development/testing.md) - Run and write tests
