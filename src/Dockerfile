# Use a base image compatible with aarch64
FROM arm64v8/python:3.10-slim-bullseye

# Set working directory
WORKDIR /app

# Copy the entire project directory to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose a command line argument for the script name
ENTRYPOINT ["python3", "final_lidar.py"]
