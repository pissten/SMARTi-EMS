ARG BUILD_FROM=ghcr.io/home-assistant/{arch}-base:latest
FROM ${BUILD_FROM}

SHELL ["/bin/ash", "-o", "pipefail", "-c"]

RUN apk add --no-cache python3 py3-pip && \
    python3 -m ensurepip || true && \
    pip3 install --no-cache-dir --upgrade pip

COPY app/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY app /app
COPY rootfs/ /

RUN chmod +x /etc/services.d/ems/run /etc/cont-init.d/00-fix-perms
ENV PYTHONUNBUFFERED=1
