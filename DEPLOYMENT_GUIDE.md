# Organ Donor Chain - Deployment Guide

## Quick Start (Railway - Recommended)

### Step 1: Prepare Your Code
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/organ-donor-chain.git
git push -u origin main
```

### Step 2: Deploy to Railway
1. Go to railway.app
2. Sign up with GitHub
3. Click "New Project" -> "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-random-secret-key-here
   PORT=8000
   ```
6. Add PostgreSQL database
7. Deploy!

### Step 3: Configure Database
1. Go to your Railway project
2. Click on the PostgreSQL service
3. Copy the connection string
4. Add to environment variables:
   ```
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

## Default Login Credentials

**Admin Account:**
- Email: admin@example.com
- Password: admin123

**IMPORTANT: Change these credentials after deployment!**

## Your App Will Be Live At:
https://your-app-name.railway.app

## Features Available:
- Hospital registration and management
- Donor and patient registration
- Smart matching system
- First-come-first-serve priority
- Unique ID system
- Real-time match notifications
- Responsive design for mobile
- Secure authentication

## Troubleshooting

### Common Issues:
1. **Database connection errors**: Check DATABASE_URL format
2. **Import errors**: Ensure all dependencies in requirements.txt
3. **Port issues**: Railway handles this automatically
4. **Static files**: Already configured in app_production.py

### Getting Help:
- Check Railway logs in dashboard
- Verify environment variables
- Test locally first
- Check database connection

## Success!
Your Organ Donor Chain system is now live on the internet!