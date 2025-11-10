# Dockerfile for the network server
FROM python:3.13-slim

# Use unbuffered output for easier debugging
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install Python dependencies (if any) from requirements.txt.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the image
COPY . .

# Expose the TCP port used by the Tic‑Tac‑Toe server
EXPOSE 5555

# Default command runs the server module
CMD ["python", "-m", "src.network_server"]

