FROM python:3.6-slim as base

RUN apt-get update -qq \
        && apt-get install -y --no-install-recommends \
        libpq-dev \
        curl \
        && apt-get autoremove -y

FROM base as builder

RUN apt-get update -qq

ADD app/requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

ADD app/ /app/
WORKDIR /app/intents

EXPOSE 5001

ENTRYPOINT ["python"]
CMD ["app.py"]