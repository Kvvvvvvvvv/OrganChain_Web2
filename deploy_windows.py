#!/usr/bin/env python3
"""
Windows-compatible deployment setup for Organ Donor Chain
This script works around Windows-specific issues
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Organ Donor Chain - Windows Deployment Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the project root directory")
        print("   (where app.py is located)")
        return
    
    print("📋 This script will:")
    print("   1. Install basic dependencies (Windows-compatible)")
    print("   2. Create production files")
    print("   3. Set up deployment configuration")
    print("   4. Create deployment instructions")
    print()
    
    # Ask for confirmation
    response = input("🤔 Do you want to continue? (y/n): ").lower().strip()
    if response != 'y':
        print("❌ Setup cancelled")
        return
    
    print("\n🔧 Starting setup...")
    
    # Step 1: Install basic dependencies (skip psycopg2 for now)
    print("\n📦 Step 1: Installing basic dependencies...")
    basic_packages = ["Flask==2.3.3", "Werkzeug==2.3.7", "python-dotenv==1.0.0"]
    
    for package in basic_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  {package} installation failed. Continuing anyway...")
    
    # Step 2: Create production files
    print("\n🔧 Step 2: Creating production files...")
    
    # Create .gitignore
    gitignore_content = """# Environment variables
.env
*.env

# Database files
*.db
*.sqlite
*.sqlite3

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Virtual environment
venv/
env/
ENV/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
*.log

# Temporary files
*.tmp
*.temp
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content.strip())
    print("✅ .gitignore created")
    
    # Create Procfile
    with open('Procfile', 'w', encoding='utf-8') as f:
        f.write("web: gunicorn app_production:app")
    print("✅ Procfile created")
    
    # Create runtime.txt
    with open('runtime.txt', 'w', encoding='utf-8') as f:
        f.write("python-3.11.0")
    print("✅ runtime.txt created")
    
    # Create requirements_production.txt
    prod_requirements = """Flask==2.3.3
Werkzeug==2.3.7
psycopg2-binary==2.9.7
gunicorn==21.2.0
python-dotenv==1.0.0
"""
    
    with open('requirements_production.txt', 'w', encoding='utf-8') as f:
        f.write(prod_requirements.strip())
    print("✅ requirements_production.txt created")
    
    # Step 3: Create deployment instructions
    print("\n📝 Step 3: Creating deployment instructions...")
    
    instructions = """# Organ Donor Chain - Deployment Guide

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
"""
    
    with open('DEPLOYMENT_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(instructions.strip())
    print("✅ Deployment guide created")
    
    # Step 4: Create environment template
    print("\n🔐 Step 4: Creating environment template...")
    
    env_template = """# Environment Variables for Production
# Copy this to .env and fill in your values

FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here-change-this
DATABASE_URL=postgresql://user:password@host:port/database
PORT=8000
"""
    
    with open('env_template.txt', 'w', encoding='utf-8') as f:
        f.write(env_template.strip())
    print("✅ Environment template created")
    
    # Final instructions
    print("\n🎉 Setup Complete!")
    print("=" * 50)
    print("\n📋 Next Steps:")
    print("1. 📚 Read DEPLOYMENT_GUIDE.md for detailed instructions")
    print("2. 🔧 Copy env_template.txt to .env and fill in your values")
    print("3. 📤 Push your code to GitHub")
    print("4. 🚀 Deploy to Railway or Render")
    print("5. 🔐 Change default admin credentials")
    print("6. 🌐 Share your live app with the world!")
    
    print("\n💡 Pro Tips:")
    print("- Start with Railway's free tier")
    print("- Use a strong secret key")
    print("- Test locally before deploying")
    print("- Monitor your app after deployment")
    
    print("\n🔗 Useful Links:")
    print("- Railway: https://railway.app")
    print("- Render: https://render.com")
    print("- GitHub: https://github.com")
    
    print("\n🎯 Your app will be live at: https://your-app-name.railway.app")
    print("\nGood luck with your deployment! 🚀")

if __name__ == "__main__":
    main()
