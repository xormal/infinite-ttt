# Dockerfile for the network server
FROM python:3.13-slim

# Use unbuffered output for easier debugging
ENV PYTHONUNBUFFERED=1

# Create a non‑root user to run the app securely
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Set working directory
WORKDIR /app

# Install Python dependencies (if any) from requirements.txt.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the image
COPY . .

# Add entrypoint script and make it executable
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose the TCP port used by the Tic‑Tac‑Toe server
EXPOSE 5555

# Allow host/port override via environment variables (default to the server defaults)
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=5555

# Default command runs the network server (environment overrides can be used by the script)
ENTRYPOINT ["docker-entrypoint.sh"]

# Switch to non‑root user
USER appuser
HEALTHCHECK --interval=30s --timeout=5s CMD nc -z localhost 5555 || exit 1
