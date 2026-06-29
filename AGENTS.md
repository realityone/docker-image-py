# Repository Guidelines

## Project Structure & Module Organization

This repository is a small Python package for parsing Docker image references. Core source code lives in `docker_image/`:

- `reference.py` implements image reference parsing and normalization.
- `regexp.py` builds the regular expressions used by the parser.
- `digest.py` validates digest algorithms and lengths.

Tests live in `tests/` and mirror the package behavior with `unittest` test cases. Package metadata and runtime dependencies are defined in `pyproject.toml`. `README.md` contains public usage examples.

## Build, Test, and Development Commands

- `python -m pip install -e .` installs the package and its `regex` dependency in editable mode.
- `python -m unittest discover -s tests` runs the test suite.
- `python -m build` builds source and wheel distributions for release checks.

Run commands from the repository root so imports resolve consistently.

## Coding Style & Naming Conventions

Use 4-space indentation and keep the existing compact, standard-library-first style. Public parser classes use `CamelCase` names such as `Reference` and `Repository`; functions, methods, variables, and test helpers use `snake_case`. Exception classes are named for the validation error they represent, for example `NameTooLong` or `DigestUnsupported`.

The package targets Python 3.10 and newer. Keep regex construction centralized in `regexp.py` rather than duplicating literal patterns across modules.

## Testing Guidelines

Tests use Python's built-in `unittest` framework. Add new test files as `tests/test_*.py`, and name test methods `test_*`. For parser behavior, follow the current table-driven style: define inputs, expected parsed fields, and expected exceptions in one place, then loop over cases.

Before submitting changes, install the package in editable mode and run `python -m unittest discover -s tests`. There is no configured coverage threshold, so focus on covering new parsing branches, digest validation paths, and error cases.

## Commit & Pull Request Guidelines

Recent history uses short, imperative commit subjects, often Conventional Commit style: `feat: optimize parsing invalid chars`, `build(licence): add Apache-2.0 license to package metadata`, or `bump 0.1.13`. Keep subjects concise and mention the affected behavior or package metadata.

Pull requests should include a brief description, related issue or motivation, test results, and examples when parser output changes. For release-related changes, call out version updates and packaging impact.
