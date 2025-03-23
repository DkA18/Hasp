# Use a base image
FROM alpine:latest

# Install dependencies
RUN apk add --no-cache python3 py3-pip redis nginx 
# Copy files
COPY ./app /opt/app
WORKDIR /opt
RUN python3 -m venv venv
WORKDIR /opt/app

RUN chmod a+x run.sh 

COPY ./app/nginx.conf /etc/nginx/nginx.conf

RUN source /opt/venv/bin/activate && pip install -r requirements.txt
EXPOSE 8099


CMD [ "sh", "./run.sh" ]
