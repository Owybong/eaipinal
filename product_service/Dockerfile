FROM python:3.10-slim

# Create non-root user with specific UID:GID
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -m -d /app appuser

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create instance directory and set permissions
RUN mkdir -p instance && \
    touch instance/products.db && \
    chown -R appuser:appgroup /app && \
    chmod -R 755 /app && \
    chmod 777 instance && \
    chmod 666 instance/products.db

# Switch to non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 5002

# Command to run the application
CMD ["python", "app.py"]
