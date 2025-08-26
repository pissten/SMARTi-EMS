# CI passes BUILD_FROM per-arch (see workflow). Fallback is amd64.
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

SHELL ["/bin/ash","-o","pipefail","-c"]

# Install Python + pip (no `apk update` — same as HomeGPT approach)
RUN apk add --no-cache python3 py3-pip && \
    ln -sf python3 /usr/bin/python && \
    python3 -m ensurepip || true && \
    pip3 install --no-cache-dir --upgrade pip

# Deps first for better layer caching
COPY app/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# App + s6 services
COPY app /app
COPY rootfs/ /

# Permissions & env
RUN chmod +x /etc/services.d/ems/run /etc/cont-init.d/00-fix-perms
ENV PYTHONUNBUFFERED=1
