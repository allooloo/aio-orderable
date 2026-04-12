# aio-orderable.ai — Ghost Router
# Built by Allooloo Technologies Corp. + Claude (Anthropic)
# MIT License | April 2026

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .
COPY catalog.json .

# Expose port
EXPOSE 8000

# Environment variables (override at runtime)
ENV MCP_ENDPOINT=""
ENV MCP_TOKEN=""

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
