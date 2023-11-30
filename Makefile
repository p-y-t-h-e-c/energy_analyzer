# Project set up under Linux or WSL [ Ubuntu ] distro

# Use at the top of the Makefile to make it work.
# Import all the environment variables from the .env file.
# If the result of $(wildcard ./.env) is not none then include .env
# 	- wildcard will return all the files that match ./.env
ifneq (,$(wildcard ./.env))
	include .env
	export
endif

# checking if git repo and initiating it if no
.PHONY: git
git:
	@if git status 2>/dev/null; then\
		echo "inside git repo";\
	else\
		git init;\
	fi;


# Package manager variable.
PACKAGE_MANAGER ?= sudo apt-get

# Linux common prerequisites variable
PREREQUISITES := sed grep awk python3-pip libpq-dev

# goes through prerequisites and install each if it's not yet installed
.PHONY: $(PREREQUISITES)
$(PREREQUISITES):
	@if which $@; then\
		echo "$@ is already installed.";\
	else\
		echo "Installing $@...";\
		$(PACKAGE_MANAGER) install $@;\
		echo "$@ installed.";\
	fi;

# installs pipx
.PHONY: pipx
pipx:
	@python3 -m pip install --user -U pipx
	@python3 -m pipx ensurepath

# Pipx dependecies variable
PIPX_DEPENDENCIES := poetry

# goes through pixp dependencies and install each if it's not yet installed
.PHONY: $(PIPX_DEPENDENCIES)
$(PIPX_DEPENDENCIES): pipx
	@if which $@; then\
		echo "$@ is already installed.";\
	else\
		echo "Installing $@...";\
		pipx install $@;\
		echo "$@ installed.";\
	fi;

# `make project-init` - installs prerequisites, pipx, poetry, git,
# 						creates virtual environment and an empty .env file
.PHONY: project-init
project-init: $(PREREQUISITES) $(PIPX_DEPENDENCIES) git
	@poetry config virtualenvs.in-project true
	@poetry install --with=dev
	@poetry run pre-commit install
	@touch .env
	@echo "Virtual environment are ready and launched using:"
	@echo "'source .venv/bin/activate'"

# `make project-update` - get and install the latest versions of the dependencies
# 						  and to update the poetry.lock file
.PHONY: project-update
project-update: pyproject.toml
	@poetry update --with=dev

# `make requirements.txt` - generate a requirements.txt file for the main code.
requirements.txt: poetry.lock
	@poetry export -f requirements.txt --without-hashes > requirements.txt


# `make requirements_dev.txt` - generate a requirements_dev.txt for the dev dependencies.
requirements_dev.txt: poetry.lock
	@poetry export -f requirements.txt --with=dev --without-hashes > requirements_dev.txt







# # Makefile settings
# # This sets the default make command to run "help", so `make` is actually `make help`
# # 	Another way to do have help run by default would be to set it as the first step
# # 	declared.
# .DEFAULT_GOAL := help
# # We will force the use of the Bourne Shell as it is the most ubiquitous/compatible.
# # If you find you need more then you can change this to a more recent shell.
# SHELL := /bin/bash

# # Import all the environment variables from the .env file.
# # This has to be in makefile format:
# # 	- https://stackoverflow.com/questions/30300830/load-env-file-in-makefile
# # 		- We've used the way in this post. It actually imports the file as if it was a
# # 			a makefile. This format works with python dotenv which is convenient!
# # If the result of $(wildcard ./.env) is not none then include .env
# # 	- wildcard will return return all the files that match ./.env
# ifneq (,$(wildcard ./.env))
# 	include .env
# 	export
# endif

# # Project settings
# ## set up
# # PROJECT_NAME:
# # 1. (cat) Print the contents of the settings file
# # 2. (grep) Filter the output of the previous function to only the lines that:
# # 	- starts with "name = "
# # 	- then has a word that contains:
# # 		- letters or spaces ([:alpha:]) OR dashes between quotes.
# # 3. (sed) Substitute the word the text that matches the sed regex with the everything
# # 	that was captured between "\(<capture_group>\)"
# PROJECT_NAME := $(shell cat pyproject.toml | grep "^name = \"[[:alpha:]-]*\"" | sed 's/^name = "\([[:alpha:]-]*\)"/\1/')
# PROJECT_NAME_SNAKE_CASE := $(shell echo "$(PROJECT_NAME)" | sed 's/-\(.*\)/_\L\1/g')

# # Get the git branch and set GIT_BRANCH to the result:
# GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null)
# # If this is not a git repo then the funciton will fail and GIT_BRANCH will return exit
# # 	code 1
# ifeq (,$(GIT_BRANCH))
#   $(error FATAL: Could not find the branch name, is this a git repo?)
# endif

# ## Folder structure:
# DOC_FOLDER := docs
# ASSETS_FOLDER := $(DOC_FOLDER)/assets

# ## Testing
# PYTEST_PASSMARK ?= 0
# PYLINT_PASSMARK ?= 0
# # This needs quotes to work, but I'm not sure why...
# MYPY_TO_TEST ?= "./app.py ./$(PROJECT_NAME_SNAKE_CASE)/ ./tests/"
# PYLINT_TO_TEST ?= app.py $(PROJECT_NAME_SNAKE_CASE)

# ## Dependencies

# ### Package Management
# # Operating system specific things
# VALID_OPERATING_SYSTEMS := linux
# OPERATING_SYSTEM ?= linux
# ## Packages available from the package manager
# PACKAGE_MANAGER_DEPENDENCIES := sed grep awk python3-pip libpq-dev
# PIPX_DEPENDENCIES := poetry

# # Will need to make this part of setting up for windows or linux.
# PACKAGE_MANAGER ?= sudo apt-get

# ## Docker
# APP_CONTAINER_NAME := $(PROJECT_NAME)-$(USER)
# APP_IMAGE_FULL_PATH := $(PROJECT_NAME):$(USER)

# POETRY_VERSION := 1.4.2
# BASE_IMAGE := python
# IMAGE_VERSION := 3.10-slim

# ## Logging
# LOG_FOLDER := .logs
# $(shell mkdir -p .logs)

# LOGGING_FILE := $(LOG_FOLDER)/makefile.log
# $(shell echo "" > $(LOGGING_FILE))

# .PHONY: test-make
# test-make:
# 	@echo "$(PROJECT_NAME_SNAKE_CASE)"
# 	@echo "$(APP_IMAGE_FULL_PATH)"

# # NOTE: This is needed as if there is a file called "all" the step will not run (since "all")
# # 	already exists
# # 	https://stackoverflow.com/questions/2145590/what-is-the-purpose-of-phony-in-a-makefile

# #all: @ Run the "cicd" pipeline.
# .PHONY: all
# all: lint tests

# #lint: @ Lint the files (and format what should be formatted)
# .PHONY: lint
# lint: pre-commit

# #tests: @ Run all python tests and static type checks
# .PHONY: tests
# tests: mypy pytest

# #help: @ List available tasks on this project
# .PHONY: help
# help:
# 	@grep -E '[a-zA-Z\.\-]+:.*?@ .*$$' $(MAKEFILE_LIST)

# #poetry.lock: @ Create/update the poetry.lock file
# poetry.lock: pyproject.toml
# 	@poetry lock





# #pytest-parallel: @ Run pytest in parallel without end to end tests, change the number of workers in the makefile.
# .PHONY: pytest-parallel
# pytest-parallel: local-postgres
# 	@echo "Running pytest."
# 	@poetry run pytest \
# 		-n=2 \
# 		-m "not e2e" \
# 		--durations=10 \
# 		--ignore=alembic \
# 		--ignore=demo \
# 		--doctest-modules \
# 		--cov=$(PROJECT_NAME_SNAKE_CASE) --cov-fail-under=$(PYTEST_PASSMARK)
# 	@echo "Pytest passed"


# #pytest: @ Run pytest and create a coverage report.
# .PHONY: pytest
# pytest: local-postgres
# 	@echo "Running pytest."
# 	@poetry run pytest \
# 		-m "not e2e" \
# 		--durations=10 \
# 		--ignore=alembic \
# 		--ignore=demo \
# 		--doctest-modules \
# 		--cov=$(PROJECT_NAME_SNAKE_CASE) --cov-fail-under=$(PYTEST_PASSMARK)
# 	@echo "Pytest passed"

# #mypy: @ Run mypy checks on the main script, main package, and tests.
# .PHONY: mypy
# mypy:
# 	@echo "Running mypy..."
# 	@poetry run mypy "$(MYPY_TO_TEST)"
# 	@echo "Mypy passed."

# # @echo "\n\nIf you get \`\"assert_never\" has incompatible type \"<Enum type>\"; expected \"NoReturn\"\` "
# # @echo "This is actually a pass, it means that the Enum was fully checked."
# # @echo "if you see \`Literal[<Enum value>]\` it means that the <enum value> was never checked."
# # @echo "They share the same error code so I can't removed one without removing the other."

# #pre-commit: @ Run pre-commit on all the files in the projcet.
# .PHONY: pre-commit
# pre-commit:
# 	@echo "Running pre-commit..."
# 	@poetry run pre-commit run --all-files
# 	@echo "pre-commit passed."

# #black: @ Run python black formatter.
# .PHONY: black
# black:
# 	@echo "Formatting with black"
# 	@poetry run black .

# #build-wheel: @ Build the package wheels.
# .PHONY: build-wheel
# build-wheel:
# 	poetry build

# #prevent-prod: @ This fails if ran on the master branch.
# .PHONY: prevent-prod
# prevent-prod:
# 	@if [ $(GIT_BRANCH) = $(PROD_BRANCH) ]; then \
# 		echo "[ERROR]: Don't mess with prod :)"; \
# 		exit 0; \
# 	fi;

# #prevent-restricted: @ This fails if we run this target on a restricted branch.
# .PHONY: prevent-restricted
# prevent-restricted: prevent-prod


# #$(PACKAGE_MANAGER_DEPENDENCIES): @ Add $(PACKAGE_MANAGER_DEPENDENCIES) if it's not installed
# .PHONY: $(PACKAGE_MANAGER_DEPENDENCIES)
# $(PACKAGE_MANAGER_DEPENDENCIES):
# 	@if which $@; then\
# 		echo "$@ is already installed.";\
# 	else\
# 		echo "Installing $@...";\
# 		$(PACKAGE_MANAGER) install $@;\
# 		echo "$@ installed.";\
# 	fi;

# #pipx: @ Add $(PIPX_DEPENDENCIES) if it's not installed
# .PHONY: pipx
# pipx:
# 	@python3 -m pip install --user pipx
# 	@python3 -m pipx ensurepath

# #$(PIPX_DEPENDENCIES): @ Add $(PIPX_DEPENDENCIES) if it's not installed
# .PHONY: $(PIPX_DEPENDENCIES)
# $(PIPX_DEPENDENCIES): pipx
# 	@if which $@; then\
# 		echo "$@ is already installed.";\
# 	else\
# 		echo "Installing $@...";\
# 		pipx install $@;\
# 		echo "$@ installed.";\
# 	fi;


# #dev-setup: @ Install the environment and pre-requisites
# #	This could fail if the python version is not up to date. If this happens you can use:
# #	`poetry use env <python_version>` (e.g. `poetry use env 3.10` for python 3.10).
# #	To install a new version of python on linux see:
# #	https://www.tecmint.com/install-python-in-ubuntu/
# #
# #	Once you've done this just rerun this command.
# .PHONY: dev-setup
# dev-setup: $(PACKAGE_MANAGER_DEPENDENCIES) $(PIPX_DEPENDENCIES) docker
# 	@poetry config virtualenvs.in-project true
# 	@poetry install --with=dev
# 	@poetry run pre-commit install
# 	@touch .env
# 	@echo "APP_ENV=LOCAL" > .env
# 	@echo "You now have a virtual environment that can be launched using
# 	@echo "'poetry run python main.py', see the poetry docs:."
# 	@echo "https://python-poetry.org/docs/"

# #copy-project: @ Copy the contents of this folder into another one.
# #	set the TARGET_DIR environment variable when running this with:
# #	`TARGET_DIR=/path/to/folder/ make copy`
# .PHONY: copy-project
# copy-project:
# 	@mkdir -p $(TARGET_DIR)
# 	@cp -ur . $(TARGET_DIR)


# #docker: @ Install docker by following the steps outlined on their website.
# #	https://docs.docker.com/engine/install/ubuntu/
# .PHONY: docker
# docker:
# 	sudo apt-get install ca-certificates curl gnupg
# 	sudo install -m 0755 -d /etc/apt/keyrings
# 	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
# 	sudo chmod a+r /etc/apt/keyrings/docker.gpg
# 	@echo \
# 		"deb [arch="$(shell dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
# 		"$(shell cat /etc/os-release | sed -n 's/^VERSION_CODENAME="*\([^"]*\)"*/\1/p')" stable" | \
# 		sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# 	@sudo apt-get update
# 	@sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# 	sudo docker run hello-world
# 	@-sudo groupadd docker
# 	@sudo usermod -aG docker $(USER)
# 	@# This echo should be before the `newgrp` command since if it's after it doesn't always work.
# 	@echo "Test the installation with \`docker run hello-world\`. You may need to log out and back in if it doesn't work."
# 	@-newgrp docker


# #docs: @ Render the documentation.
# .PHONY: docs
# docs:
# 	@echo "Rendering docs..."
# 	@bash scripts/render_docs.sh
# 	@echo "Docs rendered."


# #local-app: @ Run the app in the local environment.
# .PHONY: local-app
# local-app: local-postgres
# 	@poetry run uvicorn app:app --reload --reload-dir notifications


# #docker-app-build: @ Build the app as a docker app.
# .PHONY: docker-app-build
# docker-app-build:
# 	@echo "Building app, $(APP_IMAGE_FULL_PATH)..."
# 	docker build -t $(APP_IMAGE_FULL_PATH)\
# 		--build-arg APP_ENV=$(APP_ENV)\
# 		.
# 	@echo "Build was successful."


# #docker-app: @ Run the app in the docker container.
# .PHONY: docker-app
# docker-app: docker-app-build docker-app-rm
# 	@echo "Starting \`$(APP_CONTAINER_NAME)\`..."
# 	@docker run -d --name $(APP_CONTAINER_NAME) -p 8080:8080 $(APP_IMAGE_FULL_PATH)
# 	@echo "Container started."


# #docker-logs: @ Get the docker app logs.
# .PHONY: docker-app-logs
# docker-app-logs:
# 	docker logs $(APP_CONTAINER_NAME)


# #docker-app-stop: @ Stop the running container.
# .PHONY: docker-app-stop
# docker-app-stop:
# 	@# Can fail if container isn't active (or never started)
# 	@-docker container stop $(APP_CONTAINER_NAME)


# #docker-app-rm: @ Remove the container from the local registery.
# .PHONY: docker-app-rm
# docker-app-rm: docker-app-stop
# 	@# Can fail if the container doesn't exist (or was never created)
# 	@-docker container rm $(APP_CONTAINER_NAME)


# #local-postgres-stop: @ Stop the running container.
# .PHONY: local-postgres-stop
# local-postgres-stop:
# 	@# Can fail if container isn't active (or never started)
# 	@-docker container stop notifications-db


# #local-postgres-rm: @ Remove the postgres container from the local registery.
# .PHONY: local-postgres-rm
# local-postgres-rm: local-postgres-stop
# 	@# Can fail if the container doesn't exist (or was never created)
# 	@-docker container rm notifications-db


# #local-postgres: @ Launch a local postgres instance, to be used for testing. You may need to run `docker pull postgres` before running this if you haven't done so before.
# .PHONY: local-postgres
# local-postgres: local-postgres-rm
# 	@docker run \
# 		--name notifications-db \
# 		-p 5433:5432 \
# 		-e POSTGRES_USER=admin \
# 		-e POSTGRES_PASSWORD=password \
# 		-d \
# 		postgres
# 	@echo "Lanched a postgres instance on "
