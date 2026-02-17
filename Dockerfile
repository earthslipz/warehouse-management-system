FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

# Copy application
COPY src/ ./src

# Set Flask environment
ENV FLASK_APP=src.web_app
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Run Flask app with gunicorn (production) or flask run (development)
CMD ["python", "-m", "src.web_app"]
