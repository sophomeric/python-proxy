# Dockerfile References: https://docs.docker.com/engine/reference/builder/
FROM python:2.7.10

# Set PYTHONUNBUFFERED so output is displayed in the Docker log
ENV PYTHONUNBUFFERED=1

COPY python-proxy.py /usr/local/bin
WORKDIR /usr/local/bin

EXPOSE 53

# Run the executable
CMD ["./python-proxy.py"]
