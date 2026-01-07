# Use a modern Python version
FROM python:3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    QT_QPA_PLATFORM=offscreen

WORKDIR /app

# Install system dependencies required for PySide6 and Git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
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
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration first for caching
COPY pyproject.toml .

# Install dependencies including dev dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .[dev]

# Copy the rest of the application
COPY . .

# Default command: run tests
# We use xvfb-run to provide a virtual display for GUI tests
CMD ["xvfb-run", "-a", "pytest"]
