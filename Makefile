# yep

NAME = babao

ROOT_DIR = $(HOME)/.$(NAME).d
SRC_DIR = src
INSTALL_DIR= $(HOME)/.local
INSTALL_NAME = $(INSTALL_DIR)/bin/$(NAME)
CONFIG_DIR = config
CONFIG_FILE = $(CONFIG_DIR)/$(NAME).conf
KRAKEN_KEY_FILE = $(CONFIG_DIR)/kraken.key

export PATH := $(INSTALL_DIR)/bin:$(PATH)

INSTALL_FILES_LOG = .install_files.list
TMP_FILES = build dist temp __pycache__ $(NAME).egg-info\
            $(SRC_DIR)/$(NAME)/**/*/__pycache__ $(SRC_DIR)/$(NAME).egg-info

RM = rm -rfv
MKDIR = mkdir -pv
CP = cp -nv
ECHO = echo -e
PY = python3 -u

DEBUGER = ipython --no-confirm-exit --no-banner -i --pdb
TESTER = pytest --pdb --fulltrace
FLAKE = flake8
LINTER = pylint --rcfile=setup.cfg $(shell test $(TERM) == dumb && echo "-fparseable")
SETUP = python3 setup.py
INSTALL_FLAGS = install -O2 --user
DEVELOP_FLAGS = develop -O2 --user
RECORD_FLAGS = $(INSTALL_FLAGS) --record $(INSTALL_FILES_LOG) # --dry-run is bugged?

ifdef QUIET
SETUP += --quiet
.SILENT:
endif

ifdef DEBUG
BUILD_FLAGS += -g
EXEC = $(DEBUGER) -m $(NAME) --
else
EXEC = $(PY) -m $(NAME)
endif


.PHONY: conf install install_test install_graph clean fclean uninstall reinstall flake lint test check commit


$(NAME): | $(ROOT_DIR)
	$(SETUP) $(DEVELOP_FLAGS)
	sed -i 's|^\(#!/.*python\w*\)$$|\1 -u|' $(INSTALL_DIR)/bin/$(NAME)
	$(ECHO) '#!/bin/bash\n\n$(EXEC) "$$@"' > $(NAME)
	chmod 755 $(NAME)

$(ROOT_DIR):
	$(MKDIR) $(ROOT_DIR)/{data,log}
	$(CP) $(CONFIG_FILE) $(KRAKEN_KEY_FILE) $(ROOT_DIR)

$(INSTALL_NAME):
	$(SETUP) $(INSTALL_FLAGS)


conf: | $(ROOT_DIR)

install: $(NAME) $(INSTALL_NAME) # TODO: won't install if develop already there

install_test: install
	pip install --user .[test] # TODO

install_graph: install
	pip install --user .[graph] # TODO


clean:
	$(RM) $(TMP_FILES)

fclean: clean
	$(RM) $(NAME)

uninstall: fclean
	$(SETUP) $(RECORD_FLAGS)
	xargs $(RM) < $(INSTALL_FILES_LOG)
	$(RM) $(INSTALL_FILES_LOG)
	find $(INSTALL_DIR)/lib -name $(NAME)\* | xargs $(RM)
	find $(INSTALL_DIR)/lib -name easy-install.pth | xargs sed -i 's!\./$(NAME)-.*\.egg!!'
	make fclean #ouch
# $(RM) $(ROOT_DIR)

reinstall: uninstall install


flake:
	$(FLAKE)

lint:
	find $(SRC_DIR) -name \*.py | grep -vE '\.#|flycheck_' | xargs $(LINTER)

test:
	$(TESTER)

check: flake lint test

commit: reinstall check fclean
	git add -A .
	git diff --cached --minimal
	git commit
