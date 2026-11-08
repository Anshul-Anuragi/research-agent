FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and assets
COPY main.py .
COPY assets/ ./assets/

# Ensure output directory exists
RUN mkdir -p /app/reports

ENTRYPOINT ["python", "main.py"]
CMD ["Current state of AI Agents in 2026"]
