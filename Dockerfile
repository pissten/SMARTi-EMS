ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:14.3.3
FROM ${BUILD_FROM}

# Install Python deps
COPY app/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy application and s6 setup
COPY app /app
COPY rootfs/ /

# Make scripts executable
RUN chmod +x /etc/services.d/ems/run /etc/cont-init.d/00-fix-perms

ENV PYTHONUNBUFFERED=1
