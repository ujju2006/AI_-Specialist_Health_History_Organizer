FROM python:3.12-slim

# Prevent python from writing pyc files to disk and buffer stdout/stderr logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Set build metadata arguments
LABEL maintainer="Antigravity Team"
LABEL version="1.0.0"

# Install System level items if needed, clean cache afterwards
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source maps
COPY backend/ /app/
COPY frontend/ /app/frontend/

# Expose port and serve
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
