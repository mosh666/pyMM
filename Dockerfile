# syntax=docker/dockerfile:1.4
# Multi-stage Dockerfile for pyMediaManager CI Testing
# Supports Python 3.12, 3.13, and 3.14
# Build: docker build --build-arg PYTHON_VERSION=3.13 -t pymm:latest .

# Build argument for Python version (default 3.13)
ARG PYTHON_VERSION=3.13

# =============================================================================
# Base stage: System dependencies and common setup
# =============================================================================
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    QT_QPA_PLATFORM=offscreen \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies required for PySide6, Git, and Xvfb
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    git \
    libgl1 \
    libegl1 \
    libglib2.0-0 \
    libfontconfig1 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xinput0 \
    libxcb-xfixes0 \
    libx11-xcb1 \
    xvfb \
    xauth \
    && apt-get clean

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# =============================================================================
# Builder stage: Install Python dependencies
# =============================================================================
FROM base AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (no project)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --all-extras

# Copy project files
COPY . .

# Install project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-extras

# =============================================================================
# Test stage: Full application with all files for testing
# =============================================================================
FROM builder AS test

# Ensure venv is in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Verify installation
RUN python -c "import app; print(f'pyMediaManager version: {app.__version__}')" && \
    python -c "import PySide6.QtCore; print(f'PySide6 version: {PySide6.QtCore.__version__}')" && \
    pytest --version && \
    ruff --version && \
    mypy --version

# Default command: run tests with coverage
CMD ["bash", "-c", "xvfb-run -a pytest tests/ -v --cov=app --cov-report=term --cov-report=html --tb=short"]

# =============================================================================
# Production stage: Minimal runtime image (optional, for future use)
# =============================================================================
FROM base AS production

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python*/site-packages/ /usr/local/lib/python*/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application
COPY app app
COPY config config
COPY plugins plugins
COPY templates templates
COPY launcher.py pyproject.toml ./

# Create non-root user for security
RUN useradd -m -u 1000 pymm && chown -R pymm:pymm /app

USER pymm

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import app; print('OK')" || exit 1

# Default entrypoint
ENTRYPOINT ["python", "launcher.py"]
