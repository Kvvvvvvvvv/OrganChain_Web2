# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server/ ./

# Copy client templates and static files
COPY client/templates/ ../client/templates/
COPY client/static/ ../client/static/

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
