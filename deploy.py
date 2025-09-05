#!/usr/bin/env python3
"""
Quick deployment script for Organ Donor Chain
This script helps you prepare your app for deployment
"""

import os
import shutil
import subprocess
import sys

def check_requirements():
    """Check if required files exist"""
    required_files = [
        'app.py',
        'requirements.txt',
        'static/style.css',
        'templates/'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def create_production_files():
    """Create production-ready files"""
    print("🔧 Creating production files...")
    
    # Copy app.py to app_production.py if it doesn't exist
    if not os.path.exists('app_production.py'):
        print("📝 Creating app_production.py...")
        # The production file is already created above
    
    # Create .gitignore
    gitignore_content = """
# Environment variables
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
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    
    print("✅ Production files created")

def update_requirements():
    """Update requirements.txt with all dependencies"""
    print("📦 Updating requirements.txt...")
    
    requirements = [
        "Flask==2.3.3",
        "Werkzeug==2.3.7",
        "psycopg2-binary==2.9.7",
        "gunicorn==21.2.0",
        "python-dotenv==1.0.0"
    ]
    
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))
    
    print("✅ Requirements.txt updated")

def create_deployment_instructions():
    """Create deployment instructions"""
    instructions = """
# 🚀 Quick Deployment Instructions

## Option 1: Railway (Recommended)

1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/organ-donor-chain.git
   git push -u origin main
   ```

2. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add environment variables:
     ```
     FLASK_ENV=production
     SECRET_KEY=your-random-secret-key
     PORT=8000
     ```
   - Add PostgreSQL database
   - Deploy!

## Option 2: Render

1. **Push to GitHub** (same as above)

2. **Deploy to Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New" → "Web Service"
   - Connect your repository
   - Configure:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python app_production.py`
   - Add environment variables:
     ```
     FLASK_ENV=production
     SECRET_KEY=your-random-secret-key
     ```
   - Add PostgreSQL database
   - Deploy!

## Environment Variables

Set these in your deployment platform:

```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:pass@host:port/dbname
PORT=8000
```

## Default Admin Account

After deployment, you can login with:
- **Email**: admin@example.com
- **Password**: admin123

**⚠️ Change these credentials immediately after deployment!**

## Custom Domain (Optional)

1. Buy a domain from Namecheap, GoDaddy, etc.
2. Add CNAME record pointing to your app URL
3. Configure in your deployment platform
4. SSL certificate will be auto-generated

## Monitoring

- Check logs regularly
- Monitor database performance
- Set up backups
- Update dependencies regularly

---

**Your app will be live at: https://your-app-name.railway.app**
"""
    
    with open('DEPLOYMENT_INSTRUCTIONS.md', 'w') as f:
        f.write(instructions.strip())
    
    print("✅ Deployment instructions created")

def main():
    """Main deployment preparation function"""
    print("🚀 Organ Donor Chain - Deployment Preparation")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please fix missing files before deploying")
        return
    
    # Create production files
    create_production_files()
    
    # Update requirements
    update_requirements()
    
    # Create instructions
    create_deployment_instructions()
    
    print("\n🎉 Deployment preparation complete!")
    print("\n📋 Next steps:")
    print("1. Create a GitHub repository")
    print("2. Push your code to GitHub")
    print("3. Choose a deployment platform (Railway/Render)")
    print("4. Follow the instructions in DEPLOYMENT_INSTRUCTIONS.md")
    print("5. Set up environment variables")
    print("6. Deploy!")
    
    print("\n💡 Pro tips:")
    print("- Start with free tiers to test")
    print("- Use strong secret keys")
    print("- Monitor your app after deployment")
    print("- Set up regular backups")

if __name__ == "__main__":
    main()
