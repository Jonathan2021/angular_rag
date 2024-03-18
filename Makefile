# Default paths for configuration files
SERVER_CONFIG ?= ./rag/configurations/server_config/config_server_azure.yml
INDEX_CONFIG ?= ./rag/home/jonathan/Lab/rag/rag/configurations/store_config/config_store_azure.yml
FRONT_CONFIG ?= ./rag/path/to/frontend/config.yml

# Default paths for scripts
FRONT_DIR ?= ./rag/frontend
SERVER_SCRIPT_PATH ?= ./rag/server/server.py
INDEX_SCRIPT_PATH ?= ./rag/scripts/create_store.py

# Requirements and install commands
BACK_REQUIREMENTS_PATH ?= ./requirements.txt
# Assuming a package.json file or similar exists for frontend dependencies
FRONT_REQUIREMENTS_FILE ?= $(FRONT_DIR)/package.json

BACK_INSTALL_CMD = pip install
BACK_UNINSTALL_CMD = pip uninstall -y
FRONT_INSTALL_CMD = npm install
FRONT_UNINSTALL_CMD = npm uninstall

# Start commands
FRONT_START_CMD = ng serve
SERVER_START_CMD = python

# FLAGS
SERVER_FLAGS = --verbose
INDEX_FLAGS = --verbose

RUN_IN_BACKGROUND =

CLEAN = build dist *.egg-info $(FRONT_DIR)/node_modules

.PHONY: check-server-config check-index-config install front-install back-dependencies-install project-install front server index up clean uninstall

# Installation targets
front-install:
	@test -f $(FRONT_REQUIREMENTS_FILE) || (echo "Frontend requirements file $(FRONT_REQUIREMENTS_FILE) not found. Please ensure package.json exists." ; exit 1)
	cd $(FRONT_DIR) && $(FRONT_INSTALL_CMD)

back-dependencies-install:
	$(BACK_INSTALL_CMD) -r $(BACK_REQUIREMENTS_PATH)

project-install:
	pip install -e .

install: front-install back-dependencies-install project-install

# Checks for the existence of configuration files
check-server-config:
	@test -f $(SERVER_CONFIG) || (echo "Server configuration file $(SERVER_CONFIG) not found. Please create it." ; exit 1)

check-index-config:
	@test -f $(INDEX_CONFIG) || (echo "Index configuration file $(INDEX_CONFIG) not found. Please create it." ; exit 1)

# Targets for running each component
front:
	cd $(FRONT_DIR) && $(FRONT_START_CMD) $(RUN_IN_BACKGROUND)

server: check-server-config
	$(SERVER_START_CMD) $(SERVER_SCRIPT_PATH) --config $(SERVER_CONFIG) $(SERVER_FLAGS)

index: check-index-config
	$(SERVER_START_CMD) $(INDEX_SCRIPT_PATH) --config $(INDEX_CONFIG) $(INDEX_FLAGS)

# Target to run both frontend and backend
up:
	$(MAKE) RUN_IN_BACKGROUND="&" front
	$(MAKE) server

clean:
	# Remove Python bytecode files and directories
	-find . -type f -name "*.pyc" -exec rm -f {} +
	-find . -type d -name "__pycache__" -exec rm -rf {} +
	# Remove node_modules directory and Python build artifacts
	-rm -rf $(CLEAN)

uninstall:
	# Uninstall Python package dependencies
	-@$(BACK_UNINSTALL_CMD) -r $(BACK_REQUIREMENTS_PATH)
	# Explicit command to uninstall frontend dependencies, if needed
	# This example assumes a global uninstall is not typically required for npm packages, so it's commented out
	# -cd $(FRONT_DIR) && $(FRONT_UNINSTALL_CMD)
	# Remove node_modules directory
	-@rm -rf $(FRONT_DIR)/node_modules

