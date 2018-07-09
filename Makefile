# yep

NAME = babao
AUTHOR = JeanMax
VERSION = 0.1

ROOT_DIR = $(HOME)/.$(NAME).d
SRC_DIR = src/$(NAME)
DOC_DIR = docs
DOC_BUILD_DIR = docs/_build
TEST_DIR = test

CONFIG_DIR = config
CONFIG_FILE = $(CONFIG_DIR)/$(NAME).conf
KRAKEN_KEY_FILE = $(CONFIG_DIR)/kraken.key

TMP_FILES = build dist temp $(shell find . -name __pycache__) \
            $(NAME).egg-info $(SRC_DIR).egg-info $(DOC_DIR) .pyre

EUID = $(shell id -u)

RM = rm -rfv
MKDIR = mkdir -pv
CP = cp -nv

TESTER = pytest --fulltrace
ifndef TRAVIS
TESTER += $(shell if [ "$(TERM)" != dumb ]; then echo "--pdb"; fi)
endif
FLAKE = flake8
PYRE = pyre --source-directory $(SRC_DIR) $(shell if [ "$(TERM)" = dumb ]; then echo "--noninteractive"; fi) # server looks broken :/ $(shell python -c 'import sys; import os; print(" ".join(["--search-path " + i for i in sys.path if os.path.isdir(i)]))')
MYPY = mypy --ignore-missing-imports $(SRC_DIR)
LINTER = pylint --rcfile=setup.cfg $(shell if [ "$(TERM)" = dumb ]; then echo "-fparseable"; fi)
PIP_INSTALL = pip install $(shell if [ "$(EUID)" != 0 ] && [ "$(READTHEDOCS)$(TRAVIS)$(PYENV_VERSION)" = "" ]; then echo "--user"; fi)
PIP_UNINSTALL = pip uninstall -y

ifdef DEBUG
EXEC = ipython --no-confirm-exit --no-banner -i --pdb -m $(NAME) --
else
EXEC = python -u -m $(NAME)
endif


$(NAME): install
	printf '#!/bin/bash\n\n$(EXEC) "$$@"\n' > $(NAME)
	chmod 755 $(NAME)

$(ROOT_DIR):  # TODO: do that in setup.py / babao
	$(MKDIR) $(ROOT_DIR)/{data,log}
	$(CP) $(CONFIG_FILE) $(KRAKEN_KEY_FILE) $(ROOT_DIR)


conf: | $(ROOT_DIR)

install: conf
	$(PIP_INSTALL) .
ifndef TRAVIS
# unbufferd I/O: TODO: move to forever-babao.sh
	sed -i 's|^\(#!/.*python\w*\)$$|\1 -u|' $(shell which $(NAME))
endif

develop: install
	$(PIP_INSTALL) --editable .

install_test: conf
	$(PIP_INSTALL) .[test] # TODO

install_graph: conf
	$(PIP_INSTALL) .[graph] # TODO


clean:
	$(RM) $(TMP_FILES)

fclean: clean
	$(RM) $(NAME)

# TODO: clean all installed files
uninstall: fclean
	$(PIP_UNINSTALL) $(NAME)
# $(RM) $(ROOT_DIR)

reinstall: uninstall
	$(MAKE) $(NAME)

flake:
	$(FLAKE)

lint:
	find $(SRC_DIR) -name \*.py | grep -vE '\.#|flycheck_|eggs' | xargs $(LINTER)

pyre:
    # TODO: debug cache, opt stubs import
	$(PYRE) check 2>/dev/null | grep -v 'Undefined import \[21\]' || true

mypy:
	$(MYPY)

test:
	$(TESTER)

coverage:
	coverage run --source=$(NAME) setup.py test
	coveralls

check: lint flake pyre mypy test

$(DOC_BUILD_DIR):
	sphinx-apidoc --ext-coverage -H $(NAME) -A $(AUTHOR) -V $(VERSION) -F -o $(DOC_DIR) $(SRC_DIR)

html: $(DOC_BUILD_DIR)
	sphinx-build -M html $(DOC_DIR) $(DOC_BUILD_DIR)

man: $(DOC_BUILD_DIR)
	sphinx-build -M man $(DOC_DIR) $(DOC_BUILD_DIR)

doc: html man
	sphinx-build -M coverage $(DOC_DIR) $(DOC_BUILD_DIR)

commit: reinstall check fclean
	git add -A .
	git diff --cached --minimal
	git commit

todo:
	grep -rin todo . | grep -vE '^(Binary file|\./Makefile|\./TODO.md|\./\.travis\.yml.* make todo)'
	grep -iHn todo ./Makefile | head -n -$(shell grep -A1000 'todo:' Makefile | grep -ic todo)
	cat TODO.md

.PHONY: conf install install_test install_graph \
		clean fclean uninstall reinstall \
		flake pyre mypy lint test check commit coverage \
		doc html man todo
