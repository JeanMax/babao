# yep

NAME = babao

ROOT_DIR = ~/.$(NAME).d
SRC_DIR = src
CONFIG_DIR = config
CONFIG_FILE = $(CONFIG_DIR)/$(NAME).conf
KRAKEN_KEY_FILE = $(CONFIG_DIR)/kraken.key

INSTALL_FILES_LOG = .install_files.list
TMP_FILES = build dist temp __pycache__ $(NAME).egg-info\
            $(SRC_DIR)/$(NAME)/__pycache__ $(SRC_DIR)/$(NAME).egg-info

RM = rm -rfv
MKDIR = mkdir -pv
CP = cp -nv
ECHO = echo -e
PY = python3

DEBUGER = ipdb3
TESTER = pytest
LINTER = pylint
SETUP = $(PY) setup.py
BUILD_FLAGS = build -j4
INSTALL_FLAGS = install -O2 --user
RECORD_FLAGS = $(INSTALL_FLAGS) --record $(INSTALL_FILES_LOG) # --dry-run is bugged?

ifdef QUIET
SETUP += --quiet
.SILENT:
endif

ifdef DEBUG
BUILD_FLAGS += -g
INSTALL_FLAGS += -g
endif


.PHONY: conf all install lint test clean uninstall re

$(NAME):
	$(SETUP) $(BUILD_FLAGS)
	$(ECHO) '#!/bin/bash\n\n$(PY) -m$(NAME) "$$@"' > $(NAME)
	chmod 755 $(NAME)

conf:
	$(MKDIR) $(ROOT_DIR)/{data,log}
	$(CP) $(CONFIG_FILE) $(KRAKEN_KEY_FILE) $(ROOT_DIR)

all: $(NAME) conf

install: conf
	$(SETUP) $(INSTALL_FLAGS)

clean:
	$(RM) $(TMP_FILES)

fclean: clean
	$(RM) $(NAME)

uninstall: fclean
	$(SETUP) $(RECORD_FLAGS)
	xargs $(RM) < $(INSTALL_FILES_LOG)
	$(RM) $(INSTALL_FILES_LOG)
	find ~/.local/lib -name $(NAME)-\*\.egg | xargs $(RM)
	find ~/.local/lib -name easy-install.pth | xargs sed -i 's!\./$(NAME)-.*\.egg!!'
	make fclean
# $(RM) $(ROOT_DIR)

re: fclean all

test: re
	$(TESTER)
	$(LINTER) $(SRC_DIR)
