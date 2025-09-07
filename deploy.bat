@echo off
REM Organ Donation Management System - Windows Deployment Script

echo 🚀 Starting deployment of Organ Donation Management System...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Stop existing containers
echo 🛑 Stopping existing containers...
docker-compose down

REM Build and start the application
echo 🔨 Building and starting the application...
docker-compose up -d --build

REM Wait for the application to start
echo ⏳ Waiting for application to start...
timeout /t 10 /nobreak >nul

REM Check if the application is running
curl -f http://localhost:5000/login >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Application is running successfully!
    echo 🌐 Access the application at: http://localhost:5000
    echo 👤 Default Admin Login:
    echo    Email: admin@gmail.com
    echo    Password: 1234
) else (
    echo ❌ Application failed to start. Check the logs:
    docker-compose logs
    exit /b 1
)

echo 🎉 Deployment completed successfully!
pause
