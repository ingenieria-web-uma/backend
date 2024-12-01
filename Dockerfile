ARG PYTHON_VERSION=3.13.0
FROM python:${PYTHON_VERSION}


WORKDIR /code


COPY ./requirements.txt /code/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./models /code/models


ARG SERVICE_PATH=./app.py
COPY ${SERVICE_PATH} /code/

ENV DOCKER=1

CMD ["python", "app.py"]