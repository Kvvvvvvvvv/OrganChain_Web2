#!/bin/bash

# Organ Donation Management System - Deployment Script

echo "🚀 Starting deployment of Organ Donation Management System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start the application
echo "🔨 Building and starting the application..."
docker-compose up -d --build

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check if the application is running
if curl -f http://localhost:5000/login > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo "🌐 Access the application at: http://localhost:5000"
    echo "👤 Default Admin Login:"
    echo "   Email: admin@gmail.com"
    echo "   Password: 1234"
else
    echo "❌ Application failed to start. Check the logs:"
    docker-compose logs
    exit 1
fi

echo "🎉 Deployment completed successfully!"
