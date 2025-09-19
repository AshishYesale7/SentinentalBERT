# Dockerfile for Dataflow pipeline
FROM apache/beam_python3.11_sdk:2.52.0

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy pipeline code
COPY social_media_pipeline.py .

# Set the entrypoint
ENTRYPOINT ["python", "social_media_pipeline.py"]