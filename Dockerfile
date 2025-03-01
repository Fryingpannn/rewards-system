FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Default port is 8080, but can be overridden
ENV PORT=8080
ENV FLASK_APP=main.py
ENV FLASK_ENV=development

# Expose the default port
EXPOSE 8080

# Add entrypoint script to handle different commands
ENTRYPOINT ["./docker-entrypoint.sh"]
