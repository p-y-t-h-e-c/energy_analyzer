# Project settings
## set up
# PROJECT_NAME:
# 1. (cat) Print the contents of the settings file
# 2. (grep) Filter the output of the previous function to only the lines that:
# 	- starts with "name = "
# 	- then has a word that contains:
# 		- letters or spaces ([:alpha:]) OR dashes between quotes.
# 3. (sed) Substitute the word the text that matches the sed regex with the everything
# 	that was captured between "\(<capture_group>\)"
PROJECT_NAME := `cat pyproject.toml | grep "^name = \"[[:alpha:]-]*\"" | sed 's/^name = "\([[:alpha:]-]*\)"/\1/'`
PROJECT_NAME_SNAKE_CASE := snakecase(PROJECT_NAME)

# Get the git branch and set GIT_BRANCH to the result:
GIT_BRANCH := `git rev-parse --abbrev-ref HEAD 2>/dev/null`

## Folder structure:
DOC_FOLDER := "docs"
ASSETS_FOLDER := DOC_FOLDER + "/assets"

## Docker
APP_CONTAINER_NAME := PROJECT_NAME + "-" + `echo $USER`
APP_IMAGE_FULL_PATH := PROJECT_NAME+":"+`echo $USER`

## Testing
PYTEST_PASSMARK := "0"
PYLINT_PASSMARK := "0"

MYPY_TO_TEST := "./app.py ./"+PROJECT_NAME_SNAKE_CASE+"/ ./tests/"
PYLINT_TO_TEST := "app.py "+PROJECT_NAME_SNAKE_CASE

POETRY_VERSION := "1.4.2"
BASE_IMAGE := "python"
IMAGE_VERSION := "3.10-slim"

## Packages available from the package manager
PACKAGE_MANAGER_DEPENDENCIES := '"sed" "grep" "gawk" "python3-pip"'

## Logging
LOG_FOLDER := ".logs"
LOGGING_FILE := LOG_FOLDER+"/justfile.log"

# Logging
create-log_folder:
    mkdir -p .logs
    echo "" > {{LOGGING_FILE}}

#Run the "cicd" pipeline.
all: lint tests

#Lint the files (and format what should be formatted)
lint: pre-commit

#Run all python tests and static type checks
tests: mypy pytest

#Run pytest and create a coverage report. Can change passmark e.g run `just pytest 80` to set the passmark to 80
pytest PYTEST_PASSMARK='0': local-postgres
	echo "Running pytest."
	APP_ENV=TEST poetry run pytest \
		-m "not e2e" \
		--durations=10 \
		--ignore=alembic \
		--ignore=demo \
		--doctest-modules \
		--cov={{PROJECT_NAME_SNAKE_CASE}} --cov-fail-under={{PYTEST_PASSMARK}}
	echo "Pytest passed"

#Run pytest in parallel without end to end tests.
pytest-parallel PYTEST_PASSMARK='0': local-postgres
	echo "Running pytest."
	APP_ENV=TEST poetry run pytest \
		-n=4 \
		--durations=10 \
		--ignore=alembic \
		--ignore=demo \
		--doctest-modules \
		--cov={{PROJECT_NAME_SNAKE_CASE}} --cov-fail-under={{PYTEST_PASSMARK}}
	echo "Pytest passed"

#Run only end to end pytest and create a coverage report.
pytest-e2e PYTEST_PASSMARK='0':
	echo "Running pytest. Make sure to have the app running on localhost:8000"
	poetry run pytest \
		-m e2e \
		--durations=10 \
		--ignore=alembic \
		--ignore=demo \
		--doctest-modules \
		--cov={{PROJECT_NAME_SNAKE_CASE}} --cov-fail-under={{PYTEST_PASSMARK}}
	echo "Pytest passed"


#Run pytest without end to end or slow tests and create a coverage report.
pytest-no-slow PYTEST_PASSMARK='0': local-postgres
	echo "Running pytest."
	APP_ENV=TEST poetry run pytest \
		-m "not slow and not e2e" \
		--durations=10 \
		--ignore=alembic \
		--ignore=demo \
		--doctest-modules \
		--cov={{PROJECT_NAME_SNAKE_CASE}} --cov-fail-under={{PYTEST_PASSMARK}}
	echo "Pytest passed"

#This fails if we run this target on a restricted branch.
prevent-restricted: prevent-prod

#This fails if ran on the master branch.
prevent-prod:
	#!/bin/bash
	set -euxo
	if [ {{GIT_BRANCH}} = main ]; then echo "[ERROR]: Don't mess with prod :)"; exit 0;
	fi;

# If this is not a git repo then the funciton will fail and GIT_BRANCH will return exit code 1
valid-git-repo:
	#!/bin/bash
	set -euxo pipefail
	if [ {{GIT_BRANCH}} = feat/justfile ]; then echo 'error FATAL: Could not find the branch name, is this a git repo?';
	fi;

test-just:
    echo "{{MYPY_TO_TEST}}"
    echo "{{PYLINT_TO_TEST}}"

#Create/update the poetry.lock file
poetrylock:
	poetry lock

#Generate a requirements.txt file for the main code.
requirementstxt: poetrylock
	poetry export -f requirements.txt --without-hashes > requirements.txt

#Generate a requirements.txt for the dev dependencies.
requirements_devtxt: poetrylock
	poetry export -f requirements.txt --with=dev --without-hashes > requirements_dev.txt

#	https://docs.docker.com/engine/install/ubuntu/
#Install docker by following the steps outlined on their website.
docker:
	sudo apt-get install ca-certificates curl gnupg
	sudo install -m 0755 -d /etc/apt/keyrings
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
	sudo chmod a+r /etc/apt/keyrings/docker.gpg
	echo \
		"deb [arch="`dpkg --print-architecture`" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
		"`cat /etc/os-release | sed -n 's/^VERSION_CODENAME="*\([^"]*\)"*/\1/p'`" stable" | \
		sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
	sudo apt-get update
	sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
	sudo docker run hello-world
	-sudo groupadd docker
	sudo usermod -aG docker `echo $USER`
	# This echo should be before the `newgrp` command since if it's after it doesn't always work.
	echo "Test the installation with \`docker run hello-world\`. You may need to log out and back in if it doesn't work."
	-newgrp docker

#Render the documentation.
docs:
	echo "Rendering docs..."
	bash scripts/render_docs.sh
	echo "Docs rendered."

#	This could fail if the python version is not up to date. If this happens you can use:
#	`poetry use env <python_version>` (e.g. `poetry use env 3.10` for python 3.10).
#	To install a new version of python on linux see:
#	https://www.tecmint.com/install-python-in-ubuntu/
#
#	Once you've done this just rerun this command.
#Install the environment and pre-requisites
dev-setup: package_manager_dependencies poetry docker

#install package manager dependencies
package_manager_dependencies:
	for package in {{PACKAGE_MANAGER_DEPENDENCIES}}; do \
		echo `sudo apt-get install $package`;\echo "$package installed."; \
	done

#install pipx
pipx:
	python3 -m pip install --user pipx
	python3 -m pipx ensurepath

#install poetry
poetry: package_manager_dependencies pipx
	echo `pipx install poetry`
	poetry config virtualenvs.in-project true
	poetry install --with=dev
	poetry run pre-commit install
	echo "You now have a virtual environment that can be launched using"
	echo "'poetry run python main.py', see the poetry docs:"
	echo "https://python-poetry.org/docs/"

#Run pre-commit on all the files in the projcet.
pre-commit:
	echo "Running pre-commit..."
	poetry run pre-commit run --all-files
	echo "pre-commit passed."

#Run python black formatter.
black:
	echo "Formatting with black"
	poetry run black .

#Build the package wheels.
build-wheel:
	poetry build

#Run mypy checks on the main script, main package, and tests.
mypy:
	echo "Running mypy..."
	poetry run mypy ""{{MYPY_TO_TEST}}""
	echo "Mypy passed."

#Run the app in the local environment.
local-app: local-postgres
	poetry run uvicorn app:app --reload --reload-dir notifications

#Stop the running container.
local-postgres-stop:
	# Can fail if container isnt active (or never started)
	-docker container stop notifications-db

#Remove the postgres container from the local registery.
local-postgres-rm: local-postgres-stop
	# Can fail if the container doesnt exist (or was never created)
	-docker container rm notifications-db

#Launch a local postgres instance, to be used for testing. You may need to run `docker pull postgres` before running this if you haven't done so before.
local-postgres: local-postgres-rm
	docker run \
		--name notifications-db \
		-p 5433:5432 \
		-e POSTGRES_USER=admin \
		-e POSTGRES_PASSWORD=password \
		-d \
		postgres
	echo "Lanched a postgres instance on localhost:5433"

# Create the open api schema doc and place it in the docs directory.
open-api-schema:
    poetry run python scripts/add_open_api_schema_to_docs.py

