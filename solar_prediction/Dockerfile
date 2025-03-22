# Use a base image
FROM alpine:latest

# Install dependencies
RUN apk add --no-cache python3 py3-pip redis nginx 
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
# Copy files
COPY ./app /opt/app
WORKDIR /opt
RUN python3 -m venv venv

RUN chown -R appuser:appgroup /opt/venv

WORKDIR /opt/app

RUN chown -R appuser:appgroup /opt/app


RUN chmod a+x run.sh 
RUN mkdir -p /var/lib/nginx /var/log/nginx /run/nginx \
    && chown -R appuser:appgroup /var/lib/nginx /var/log/nginx /run/nginx /etc/nginx /data

COPY ./app/nginx.conf /etc/nginx/nginx.conf
USER appuser
RUN source /opt/venv/bin/activate && pip install -r requirements.txt
EXPOSE 8099


CMD [ "sh", "./run.sh" ]
