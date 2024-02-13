[![doc](https://github.com/mscheltienne/well-play-teen/actions/workflows/doc.yaml/badge.svg?branch=main)](https://github.com/mscheltienne/well-play-teen/actions/workflows/doc.yaml)

# WELL-PLAY TEEN

Website build for the research project Well-Play Teen. The build uses sphinx and
requires Python 3.9 or above. The requirements can be installed with:

```
$ pip install -r requirements.txt
```

Commands:
- Build the documentation: `make html`
- Open the build in a browser: `make view`
- Delete the build: `make clean`
- Check all links: `make linkcheck`
- Parse the output from linkcheck for errors: `make linkcheck-grep`

This repository supports the pre-commit framework for linting.

```
$ pip install pre-commit
$ pre-commit install
```
