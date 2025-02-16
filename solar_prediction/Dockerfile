# Use a base image
FROM alpine:latest

# Install dependencies
RUN apk add --no-cache python3 py3-pip

# Copy files
COPY app /opt/app
WORKDIR /opt/app
RUN python3 -m venv venv
RUN source venv/bin/activate && pip install -r requirements.txt
EXPOSE 5000