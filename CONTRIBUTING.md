# Contributing Guidelines

First off, thanks for considering to contribute to this project!

These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Git hooks

We use git hooks through [pre-commit](https://pre-commit.com/) to enforce and automatically check some "rules". Please install them (`pre-commit install`) before to push any commit.

See the relevant configuration file: `.pre-commit-config.yaml`.

## Code Style

Make sure your code *roughly* follows [PEP-8](https://www.python.org/dev/peps/pep-0008/) and keeps things consistent with the rest of the code:

- sorted imports: [isort](https://pycqa.github.io/isort/) is used to sort imports
- static analysis: [flake8](https://flake8.pycqa.org/en/latest/) is used to catch some dizziness and keep the source code healthy.

## Commit linter

We use the linter [commitizen](https://github.com/commitizen-tools/commitizen) with the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) configuration (the default one).

The commit message writing process can be guided by using `cz commit` instead of `git commit`.
