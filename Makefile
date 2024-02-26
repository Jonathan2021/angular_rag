# Default paths for configuration files
SERVER_CONFIG ?= /home/jonathan/Lab/rag/rag/configurations/server_config/config_server_azure.yml
INDEX_CONFIG ?= /home/jonathan/Lab/rag/rag/configurations/store_config/config_store_azure.yml
FRONT_CONFIG ?= /path/to/frontend/config.yml

# Default paths for scripts
# Assuming there needs to be a FRONT_SCRIPT_PATH similar to the SERVER_SCRIPT_PATH and INDEX_SCRIPT_PATH
FRONT_DIR ?= ./rag/frontend 
SERVER_SCRIPT_PATH ?= ./rag/server/server.py
INDEX_SCRIPT_PATH ?= ./rag/scripts/create_store.py

# Requirements and install commands
BACK_REQUIREMENTS_PATH ?= ./requirements.txt

BACK_INSTALL_CMD = pip install
FRONT_INSTALL_CMD = npm install

# Start commands
# Assuming FRONT_START_CMD needs a specific command; using a generic placeholder
FRONT_START_CMD = ng serve 
SERVER_START_CMD = python

# FLAGS
SERVER_FLAGS = --verbose
INDEX_FLAGS = --verbose

RUN_IN_BACKGROUND =

.PHONY: check-server-config check-index-config install front-install back-dependencies-install project-install front server index up check-front-config

# Installation targets
front-install:
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

check-front-config:
	@test -f $(FRONT_CONFIG) || (echo "Frontend configuration file $(FRONT_CONFIG) not found. Please create it." ; exit 1)

# Targets for running each component
front: #check-front-config
	cd $(FRONT_DIR) && $(FRONT_START_CMD) $(RUN_IN_BACKGROUND) #--config $(FRONT_CONFIG)

server: check-server-config
	$(SERVER_START_CMD) $(SERVER_SCRIPT_PATH) --config $(SERVER_CONFIG) $(SERVER_FLAGS)

index: check-index-config
	$(SERVER_START_CMD) $(INDEX_SCRIPT_PATH) --config $(INDEX_CONFIG) $(INDEX_FLAGS)

# Target to run both frontend and backend
up:
	$(MAKE) RUN_IN_BACKGROUND="&" front
	$(MAKE) server


