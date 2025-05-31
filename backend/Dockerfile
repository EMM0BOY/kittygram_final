FROM python:3.10-slim

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       gettext \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy project code
COPY backend /app/backend

# Collect static files (if any)
# RUN python backend/manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run via Gunicorn
CMD ["gunicorn", "backend.config.wsgi:application", "--bind", "0.0.0.0:8000"]