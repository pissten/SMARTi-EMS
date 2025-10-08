ARG BUILD_FROM
FROM ${BUILD_FROM}

# Bruk /bin/sh (finnes på både Alpine & Debian)
SHELL ["/bin/sh", "-c"]

# Installer Python + venv uansett base
RUN set -ex; \
    if command -v apt-get >/dev/null 2>&1; then \
        apt-get update && \
        apt-get install -y --no-install-recommends python3 python3-pip python3-venv && \
        rm -rf /var/lib/apt/lists/*; \
    elif command -v apk >/dev/null 2>&1; then \
        apk add --no-cache python3 py3-pip py3-virtualenv; \
    else \
        echo "Unsupported base image"; exit 1; \
    fi

# Copy requirements og installer i venv (renest, unngår PEP 668)
COPY app/requirements.txt /app/requirements.txt
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --prefer-binary -r /app/requirements.txt
ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1

# Copy app + s6 services
COPY app /app
COPY rootfs/ /
RUN chmod +x /etc/services.d/ems/run /etc/cont-init.d/00-fix-perms

EXPOSE 8099
