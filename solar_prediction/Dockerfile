# Use a base image
FROM alpine:latest

# Install dependencies
RUN apk add --no-cache python3 py3-pip

# Copy files
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Start the add-on
CMD [ "/run.sh" ]
