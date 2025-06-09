FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for JSON storage
RUN mkdir -p data

# Expose the port the app runs on
EXPOSE 5004

# Command to run the application
CMD ["python", "app.py"] 