# Use official Python base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the port your app runs on
EXPOSE 5000

# Start the app using Gunicorn
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:5000", "app:create_app()"]
