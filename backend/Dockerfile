# 1. Builder Stage: Install dependencies
FROM python:3.13.5-slim-bookworm AS builder

# Install system dependencies required for building and downloading
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv - a fast Python package installer
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set up a virtual environment
WORKDIR /backend
RUN uv venv

# Copy the dependency definition and lock file
COPY pyproject.toml uv.lock ./

# Install dependencies from the lock file.
RUN --mount=type=cache,target=/root/.cache/uv \
    . .venv/bin/activate && \
    uv sync --no-dev

# Copy the rest of the application code
COPY . .


# 2. Final Stage: Create the production image
FROM python:3.13.5-slim-bookworm AS final

# Install runtime system dependencies for libraries like docling (PDFs) and easyocr (images)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /backend

# Create a non-root user for security
RUN useradd  --shell /usr/sbin/nologin backend && \
    mkdir -p /data && \
    chown -R backend:backend /backend /data

# Copy the virtual environment from the builder stage
COPY --from=builder /backend/.venv ./.venv
# Copy the application code from the builder stage
COPY --from=builder /backend/ ./

# Ensure the 'backend' user owns all files
RUN chown -R backend:backend /backend

# Switch to the non-root user
USER backend

# Make the virtual environment's binaries accessible
ENV PATH="/backend/.venv/bin:${PATH}"
ENV PYTHONPATH=/backend

# Expose the port the app runs on
EXPOSE 8000

# CMD is commented out in the original, keeping it that way as compose.yml overrides it.
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
