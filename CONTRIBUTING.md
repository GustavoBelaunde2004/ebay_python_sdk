# Contributing to `ebay_rest`

Thanks for helping improve the SDK! Please follow these guidelines to keep things consistent.

## Getting started

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dependencies in editable mode:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate
   pip install -e ".[dev]"
   ```
3. Copy `ENV_TEMPLATE.txt` to `.env` and fill in your sandbox credentials if you need to run the example scripts.

## Running tests and linting

```bash
pytest
ruff check .
black .
```

Please ensure `pytest` passes before opening a PR. If you add functionality, include unit tests in `tests/`.

## Commit and PR guidelines

- Keep commits focused and descriptive.
- Update or add documentation when you change public behavior.
- Mention any new environment variables or scripts in the README.
- For features touching Sell APIs, describe how to exercise them in the sandbox.

## Reporting issues

If you hit a bug or need a feature, open an issue with:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)

Thanks for contributing!

