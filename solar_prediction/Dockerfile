# Use a base image
FROM alpine:latest

# Install dependencies
RUN apk add --no-cache python3 py3-pip

# Copy files
COPY run.sh /opt/run.sh
RUN chmod a+x /opt/run.sh
COPY app /opt/app
WORKDIR /opt
RUN python3 -m venv venv
RUN source venv/bin/activate && pip install -r app/requirements.txt
EXPOSE 5000
CMD [ "sh", "run.sh" ]