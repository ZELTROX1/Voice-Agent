# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
# COPY requirements.txt .

RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install "livekit-agents[groq,cartesia,silero,turn-detector]~=1.0"  "livekit-plugins-noise-cancellation~=0.2"  "python-dotenv" "langchain_community"

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Expose the port (adjust if your agent uses a different port)
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# RUN pip install livekit-agents[deepgram,groq,cartesia,silero,turn-detector]~=1.0


# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the application
RUN python3 main.py download-files
CMD ["python", "main.py", "dev"]