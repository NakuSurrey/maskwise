# ─── STAGE 1: builder ───────────────────────────────────────────
# this stage compiles wheels for any C-extension packages
# builder image is bigger, but we throw it away at the end
FROM python:3.11-slim AS builder

# build deps — only needed to compile wheels, NOT in final image
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# install python deps into /install — copy that whole tree to the runtime stage
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ─── STAGE 2: runtime ───────────────────────────────────────────
# this stage is what actually runs in production
# no build tools, no pip cache, no apt cache — minimal attack surface
FROM python:3.11-slim AS runtime

# create non-root user — NHS lesson: never run containers as root
RUN groupadd -r maskwise && useradd -r -g maskwise -d /app -s /sbin/nologin maskwise

WORKDIR /app

# copy compiled wheels from the builder stage
COPY --from=builder /install /usr/local

# copy app source code
COPY app/ ./app/

# make the app folder owned by the non-root user
RUN chown -R maskwise:maskwise /app

# switch to non-root for runtime
USER maskwise

# port the app listens on inside the container
EXPOSE 8005

# healthcheck — used by docker to know if the container is alive
# nginx outside also pings this same path
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8005/health').read()" || exit 1

# uvicorn runs the app
# --workers 1 — single worker is plenty for stub phase
# --host 0.0.0.0 — bind to all interfaces INSIDE the container (docker-compose maps to 127.0.0.1 on host)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005", "--workers", "1"]
