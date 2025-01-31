FROM python:3.10-slim

# Checkout and install dagster libraries needed to run the gRPC server
# and also both dagster-webserver and the dagster-daemon.
# Does not need to have access to any pipeline code.

RUN pip install --upgrade pip
RUN pip install \
    dagster \
    dagster-graphql \
    dagster-webserver \
    dagster-postgres \
    dagster-docker

# Set $DAGSTER_HOME and copy dagster instance and workspace YAML there
ENV DAGSTER_HOME=/opt/dagster/app

RUN mkdir -p $DAGSTER_HOME

COPY dagster.yaml workspace.yaml $DAGSTER_HOME

# Installing project dependenciec and exposing repository
# to dagster-webserver and dagster-daemon, and to load the DagsterInstance

# Add repository code
WORKDIR /opt/dagster/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY energy_analyzer ./energy_analyzer

# Run dagster gRPC server on port 4000

EXPOSE 4000

# CMD allows this to be overridden from run launchers or executors that want
# to run other commands against your repository
CMD ["dagster", "api", "grpc", "-h", "0.0.0.0", "-p", "4000",  "-f", "energy_analyzer/app.py"]
