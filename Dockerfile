FROM python:3.12-slim AS upstream-binary
ARG CDCX_VERSION=1.2.6
ARG TARGETARCH=amd64
COPY scripts/install_cdcx.py /tmp/install_cdcx.py
RUN python /tmp/install_cdcx.py "$CDCX_VERSION" "$TARGETARCH" /out/cdcx

FROM python:3.12-slim
RUN pip install --no-cache-dir "mcp[cli]>=1.26,<2"
COPY --from=upstream-binary /out/cdcx /usr/local/bin/cdcx
COPY server.py /app/server.py
RUN useradd -u 1000 -m -d /home/cdcx cdcx && mkdir -p /app && chown 1000:1000 /app
USER 1000:1000
ENV HOME=/home/cdcx XDG_CONFIG_HOME=/home/cdcx/.config PYTHONUNBUFFERED=1
WORKDIR /home/cdcx
EXPOSE 18767
ENTRYPOINT ["python","/app/server.py"]
LABEL org.opencontainers.image.source="https://github.com/GodsQuantum/Cloud9-CDCX-Paper-MCP" org.opencontainers.image.title="Cloud9-CdcxPaper-MCP" org.opencontainers.image.description="Five safe paper trading MCP tools built on official Crypto.com cdcx CLI" org.opencontainers.image.licenses="MIT"
