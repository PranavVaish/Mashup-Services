# 1. Base Image (REQUIRED at the top)
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# 2. Install FFmpeg
# We combine 'update' and 'install' in one RUN command to avoid errors
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# 3. Fix Permissions (Fixes your 'chmod' error)
# Note the 'RUN' instruction at the start is mandatory
RUN mkdir -p temp_audio uploads && \
    chmod 777 temp_audio uploads

# Expose port and start app
EXPOSE 7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]