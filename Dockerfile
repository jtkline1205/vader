# Use a base image with Python
FROM python:3.9

# Set the working directory
WORKDIR /usr/src/app

# Copy the Python script and dependencies (if any)
COPY app.py .

# Install required dependencies
RUN pip install Flask

# Expose the port your service will run on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]