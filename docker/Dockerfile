FROM python:3.11-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements.txt from src/ (relative to Dockerfile location)
COPY src/requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy ALL source files from src/ into /app
COPY src/ .

# Expose port
EXPOSE 5000
# Run the app
CMD ["python", "main.py"]