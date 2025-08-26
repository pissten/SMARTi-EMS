ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:14.3.3
FROM ${BUILD_FROM}

# Install Python deps
COPY app/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy application
COPY app /app

# s6 services and init
COPY rootfs/ /

# Make sure scripts are executable
RUN chmod +x /etc/services.d/ems/run /etc/cont-init.d/00-fix-perms

# Environment
ENV PYTHONUNBUFFERED=1

# s6 will start our service via /etc/services.d/ems/run
