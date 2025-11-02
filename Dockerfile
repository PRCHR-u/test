# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy requirements folder
COPY requirements/ ./requirements/

# Install dependencies from the specific path
RUN pip install --no-cache-dir -r ./requirements/base.txt

# Copy the rest of the project
COPY . .

# Make the entrypoint script executable inside the image
RUN chmod +x /app/entrypoint.sh

# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
