FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .
COPY .env* ./

# Expose the port
EXPOSE 8000

# Run the server
CMD ["python", "server.py"]
