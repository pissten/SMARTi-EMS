# Python preinstalled (multi-arch manifest)
ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:14.3.3
FROM ${BUILD_FROM}

# If the base uses ash, leave this out; it's optional
# SHELL ["/bin/ash","-o","pipefail","-c"]

# Python deps
COPY app/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# App + s6 services
COPY app /app
COPY rootfs/ /

# Permissions & env
RUN chmod +x /etc/services.d/ems/run /etc/cont-init.d/00-fix-perms
ENV PYTHONUNBUFFERED=1
