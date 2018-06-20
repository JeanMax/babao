# yep

NAME = babao


ROOT_DIR = $(HOME)/.$(NAME).d
SRC_DIR = src
DOC_DIR = doc

CONFIG_DIR = config
CONFIG_FILE = $(CONFIG_DIR)/$(NAME).conf
KRAKEN_KEY_FILE = $(CONFIG_DIR)/kraken.key

TMP_FILES = build dist temp $(shell find . -name __pycache__) \
            $(NAME).egg-info $(SRC_DIR)/$(NAME).egg-info

RM = rm -rfv
MKDIR = mkdir -pv
CP = cp -nv
PY = python -u

EUID = $(shell id -u)

DEBUGER = ipython --no-confirm-exit --no-banner -i --pdb
TESTER = pytest --fulltrace
ifndef TRAVIS
TESTER += $(shell if [ "$(TERM)" != dumb ]; then echo "--pdb"; fi)
endif
FLAKE = flake8
LINTER = pylint --rcfile=setup.cfg $(shell if [ "$(TERM)" = dumb ]; then echo "-fparseable"; fi)
PIP_INSTALL = pip install $(shell if [ "$(EUID)" != 0 ] && [ "$(TRAVIS)" = "" ] && [ "$(PYENV_VERSION)" = "" ]; then echo "--user"; fi)
PIP_UNINSTALL = pip uninstall -y

ifdef DEBUG
EXEC = $(DEBUGER) -m $(NAME) --
else
EXEC = $(PY) -m $(NAME)
endif


.PHONY: conf install install_test install_graph clean fclean uninstall reinstall flake lint test check commit coverage doc

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

uninstall: fclean
	$(PIP_UNINSTALL) $(NAME)
# $(RM) $(ROOT_DIR)

reinstall: uninstall
	$(MAKE) $(NAME)

flake:
	$(FLAKE)

lint:
	find $(SRC_DIR) -name \*.py | grep -vE '\.#|flycheck_' | xargs $(LINTER)

test:
	$(TESTER)

coverage:
	coverage run --source=$(NAME) setup.py test
	coveralls

check: flake lint test

doc:
	sphinx-apidoc --ext-coverage -H $(NAME) -A JeanMax -V 0.1 -F -o $(DOC_DIR) $(SRC_DIR)/$(NAME)
	sphinx-build -M html $(DOC_DIR) $(DOC_DIR)/_build
	sphinx-build -M man $(DOC_DIR) $(DOC_DIR)/_build
	sphinx-build -M coverage $(DOC_DIR) $(DOC_DIR)/_build

commit: reinstall check fclean
	git add -A .
	git diff --cached --minimal
	git commit
