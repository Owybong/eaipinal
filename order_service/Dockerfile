FROM python:3.10-slim

WORKDIR /app

# Install wait-for-it
RUN apt-get update
RUN apt-get install -y wget
RUN wget -O /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for JSON storage with proper permissions
RUN mkdir -p data && chmod 777 data

# Expose the port the app runs on
EXPOSE 5004

# Use wait-for-it to ensure MySQL is ready
CMD ["sh", "-c", "wait-for-it.sh mysql:3306 -t 60 -- python app.py"] 