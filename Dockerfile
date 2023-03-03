FROM python:3-slim-bullseye

COPY requirements.txt /
RUN pip3 install -r requirements.txt && pip cache purge && rm requirements.txt

WORKDIR /app
COPY diagnosis diagnosis
COPY plugins plugins
COPY config config

CMD [ "python3", "-m", "diagnosis", "headless" ]
