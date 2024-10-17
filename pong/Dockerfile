FROM        python:3.11.7-bullseye

RUN         apt update -y && \
            apt upgrade -y && \
			apt install curl vim lsof -y

RUN         mkdir -p /microservice/pong/

COPY        . /microservice/pong/

RUN         pip install --upgrade pip

RUN			pip install --no-cache-dir -r microservice/pong/requirements.txt

WORKDIR     /microservice/pong/

CMD         [ "bash", "./tools/microservice-run.sh" ]
