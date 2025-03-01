# Use a base image
FROM alpine:latest

# Install dependencies
RUN apk add --no-cache python3 py3-pip redis
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
# Copy files
COPY ./app /opt/app
WORKDIR /opt
RUN python3 -m venv venv

RUN chown -R appuser:appgroup /opt/venv

WORKDIR /opt/app

RUN chown -R appuser:appgroup /opt/app


USER appuser
RUN source /opt/venv/bin/activate && pip install -r requirements.txt
EXPOSE 5000