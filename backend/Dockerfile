FROM python:3.13.5-slim-bookworm


RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*


ADD https://astral.sh/uv/install.sh /uv-installer.sh


RUN sh /uv-installer.sh && rm /uv-installer.sh


ENV PATH="/root/.local/bin/:$PATH"

# Set the working directory
WORKDIR /backend


COPY pyproject.toml uv.lock* ./


RUN uv sync --locked


ENV PYTHONPATH=/backend


COPY . .


EXPOSE 8000

# RUN PROJECT
#CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
#CMD [ "uv","run","fastapi","dev","main.py", "--host", "0.0.0.0", "--port", "8000" ]
