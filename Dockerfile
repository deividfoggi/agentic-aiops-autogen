FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt first for better cache utilization
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY src/ .

# Expose port 8080
EXPOSE 8080

# Command to run the application
CMD ["python", "main.py"]