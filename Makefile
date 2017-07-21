# yep

NAME = babao

ROOT_DIR = $(HOME)/.$(NAME).d
SRC_DIR = src
INSTALL_DIR= $(HOME)/.local/
CONFIG_DIR = config
CONFIG_FILE = $(CONFIG_DIR)/$(NAME).conf
KRAKEN_KEY_FILE = $(CONFIG_DIR)/kraken.key

export PATH := $(INSTALL_DIR)/bin:$(PATH)

INSTALL_FILES_LOG = .install_files.list
TMP_FILES = build dist temp __pycache__ $(NAME).egg-info\
            $(SRC_DIR)/$(NAME)/__pycache__ $(SRC_DIR)/$(NAME).egg-info

RM = rm -rfv
MKDIR = mkdir -pv
CP = cp -nv
ECHO = echo -e
PY = python3

DEBUGER = ipython --no-confirm-exit --no-banner -i --pdb
TESTER = pytest --pdb --fulltrace
FLAKE = flake8
LINTER = pylint --rcfile=setup.cfg $(shell test $(TERM) == dumb && echo "-fparseable")
SETUP = python3 setup.py
BUILD_FLAGS = build -j4
INSTALL_FLAGS = install -O2 --user
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


.PHONY: conf all install lint test check clean fclean uninstall rebuild reinstall commit

$(NAME):
	$(SETUP) $(BUILD_FLAGS)
	$(ECHO) '#!/bin/bash\n\n$(EXEC) "$$@"' > $(NAME)
	chmod 755 $(NAME)

conf:
	$(MKDIR) $(ROOT_DIR)/{data,log}
	$(CP) $(CONFIG_FILE) $(KRAKEN_KEY_FILE) $(ROOT_DIR)

all: $(NAME) conf

install: all
	$(SETUP) $(INSTALL_FLAGS)

install_tests: all
	pip install --user .[test] # TODO

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

rebuild: fclean all

reinstall: uninstall install

flake:
	$(FLAKE)

lint:
	find $(SRC_DIR) -name \*.py | grep -vE '\.#|flycheck_' | xargs $(LINTER)

test:
	$(TESTER)

check: reinstall flake lint test

commit: check fclean
	git add -A .
	git diff --cached --minimal
	git commit
