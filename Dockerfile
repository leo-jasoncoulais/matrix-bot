FROM python:3.13-slim

WORKDIR /app

RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -s /bin/bash appuser

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg \
        -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    . /etc/os-release && \
    ARCH=$(dpkg --print-architecture) && \
    printf "Types: deb\n\
URIs: https://download.docker.com/linux/debian\n\
Suites: %s\n\
Components: stable\n\
Architectures: %s\n\
Signed-By: /etc/apt/keyrings/docker.asc\n" \
        "$VERSION_CODENAME" "$ARCH" \
        > /etc/apt/sources.list.d/docker.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg docker-ce-cli docker-compose-plugin curl zstd dos2unix libolm-dev && \
    rm -rf /var/lib/apt/lists/*
    
    
RUN curl -fsSL https://ollama.com/install.sh | sh && \
    mkdir -p /home/appuser/.ollama && \
    chown -R appuser:appgroup /home/appuser/.ollama

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appgroup . .

COPY entrypoint.sh /entrypoint.sh
RUN dos2unix /entrypoint.sh && \
    chmod +x /entrypoint.sh

USER appuser

ENV OLLAMA_MODELS=/home/appuser/.ollama

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]