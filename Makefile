# Minimal makefile for Sphinx documentation

SPHINXOPTS    ?= -nWT --keep-going
SPHINXBUILD   ?= sphinx-build

.PHONY: help Makefile clean html html-noplot linkcheck linkcheck-grep view

first_target: help

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html             to make standalone HTML files"
	@echo "  clean            to clean HTML files"
	@echo "  linkcheck        to check all external links for integrity"
	@echo "  linkcheck-grep   to grep the linkcheck result"
	@echo "  view             to view the built HTML"

html:
	$(SPHINXBUILD) src build/html -b html $(SPHINXOPTS)

clean:
	rm -rf build

linkcheck:
	$(SPHINXBUILD) src build/linkcheck -b linkcheck

linkcheck-grep:
	@! grep -h "^.*:.*: \[\(\(local\)\|\(broken\)\)\]" build/linkcheck/output.txt

view:
	@python -c "import webbrowser; webbrowser.open_new_tab('file://$(PWD)/build/html/index.html')"
