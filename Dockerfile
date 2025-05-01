FROM python:3.13-slim

# Set environment variables:
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disk (equivalent to python -B option)
# - PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY . .

RUN pip install --upgrade pip  \
    && pip install --no-cache-dir -r requirements.txt

RUN python manage.py makemigrations
RUN python manage.py migrate

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Use gunicorn as the entry point to serve the app. Adjust the number of workers as necessary.
CMD ["gunicorn", "Linkedrite.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
