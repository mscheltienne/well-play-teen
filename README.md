[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![codecov](https://codecov.io/gh/mscheltienne/well-play-teen/graph/badge.svg?token=ufvGyLnUMY)](https://codecov.io/gh/mscheltienne/well-play-teen)
[![tests](https://github.com/mscheltienne/well-play-teen/actions/workflows/pytest.yaml/badge.svg?branch=main)](https://github.com/mscheltienne/well-play-teen/actions/workflows/pytest.yaml)
[![doc](https://github.com/mscheltienne/well-play-teen/actions/workflows/doc.yaml/badge.svg?branch=main)](https://github.com/mscheltienne/well-play-teen/actions/workflows/doc.yaml)

# WELL-PLAY TEEN

Website build and code for the research project Well-Play Teen. Requires Python 3.10 or
above.

## Website

The [website](https://well-play-teen.org/) build uses `sphinx`. Requirements can be
installed with the `[doc]` key of this python package.

Build commands from the `doc` folder:
- Build the documentation: `make html`
- Open the build in a browser: `make view`
- Delete the build: `make clean`
- Check all links: `make linkcheck`
- Parse the output from linkcheck for errors: `make linkcheck-grep`

## Linting

This repository supports the pre-commit framework for linting.

```bash
$ pip install pre-commit
$ pre-commit install
```
