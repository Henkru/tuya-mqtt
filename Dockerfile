FROM python:3.9.13-alpine3.16

COPY ./src/__main__.py ./requirements.txt /usr/src/app/

RUN apk add --no-cache gcc libc-dev && \
    pip install --no-cache-dir -r /usr/src/app/requirements.txt

WORKDIR /data
CMD ["python", "-u", "/usr/src/app"]
