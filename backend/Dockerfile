FROM python:3.13.5-slim-bookworm

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Set the working directory
WORKDIR /backend

# Copy only the dependency definition files first
COPY pyproject.toml uv.lock* ./

# Install dependencies based on the lock file.
# This layer is cached and only re-runs if these files change.
RUN uv sync --locked

# Now copy the rest of the application code
COPY . .

# EXPOSE PORT
EXPOSE 8000

# RUN PROJECT
#CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD [ "uv","run","fastapi","dev","main.py", "--host", "0.0.0.0", "--port", "8000" ]
