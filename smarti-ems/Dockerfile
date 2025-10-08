ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-debian:bookworm
FROM ${BUILD_FROM}

SHELL ["/bin/bash","-o","pipefail","-c"]

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY app/requirements.txt /app/requirements.txt

# Install deps (prefer wheels)
RUN pip3 install --no-cache-dir --prefer-binary --break-system-packages -r /app/requirements.txt

# Copy app + s6 services
COPY app /app
COPY rootfs/ /

RUN chmod +x /etc/services.d/ems/run /etc/cont-init.d/00-fix-perms
ENV PYTHONUNBUFFERED=1
