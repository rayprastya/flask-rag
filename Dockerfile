# Use official Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app will run on
EXPOSE 8001

# Start the app using Gunicorn
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8001", "app:create_app()"]
