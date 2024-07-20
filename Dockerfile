# Use an official Python runtime as a parent image
FROM python:3.8-slim as builder

# Set environment variables:
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disk (equivalent to python -B option)
# - PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for Python packages with native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libffi-dev \
    libssl-dev \
    cargo \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry for Python package management
RUN pip install --upgrade pip && pip install poetry

# Set the working directory in the container
WORKDIR /app

# Copy the Python dependency files to the container
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry:
# - virtualenvs.create false: Prevents Poetry from creating a virtual environment inside the Docker container
# Install runtime dependencies only (no development dependencies)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev --no-root

# Start a new build stage for the final image
FROM python:3.8-slim as final

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set the working directory in the container
WORKDIR /app

# Copy the Django project files to the container
COPY . /app/

RUN python manage.py makemigrations
RUN python manage.py migrate

# Collect static files
RUN python manage.py collectstatic --noinput


# Expose the port the app runs on
EXPOSE 8000

# Use gunicorn as the entry point to serve the app. Adjust the number of workers as necessary.
CMD ["gunicorn", "LinkedInAi.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]