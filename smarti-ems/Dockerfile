# DO NOT embed {arch} here. We pass BUILD_FROM from CI.
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

SHELL ["/bin/ash", "-o", "pipefail", "-c"]

# Python + pip on Alpine
RUN apk add --no-cache python3 py3-pip && \
    python3 -m ensurepip || true && \
    pip3 install --no-cache-dir --upgrade pip

# Python deps
COPY app/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# App + s6 services
COPY app /app
COPY rootfs/ /

RUN chmod +x /etc/services.d/ems/run /etc/cont-init.d/00-fix-perms
ENV PYTHONUNBUFFERED=1
