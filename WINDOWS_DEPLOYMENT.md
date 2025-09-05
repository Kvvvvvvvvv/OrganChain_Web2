# Windows Deployment Guide for Organ Donor Chain

## 🚀 Quick Deployment (Windows-Friendly)

### Step 1: Install Basic Dependencies
```bash
pip install Flask Werkzeug python-dotenv
```

### Step 2: Run Windows Setup
```bash
python deploy_windows.py
```

### Step 3: Deploy to Railway (Recommended)

#### 3.1: Create GitHub Repository
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/organ-donor-chain.git
git push -u origin main
```

#### 3.2: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-random-secret-key-here
   PORT=8000
   ```
6. Add PostgreSQL database
7. Deploy!

## 🔧 Windows-Specific Notes

### PostgreSQL Installation (Optional for Local Testing)
If you want to test PostgreSQL locally on Windows:

1. **Download PostgreSQL**: https://www.postgresql.org/download/windows/
2. **Install with default settings**
3. **Add to PATH**: Add PostgreSQL bin directory to your system PATH
4. **Test installation**: `psql --version`

### Alternative: Use SQLite for Development
Your app already supports SQLite for local development. PostgreSQL is only needed for production deployment.

## 🌐 Your App Will Be Live At:
`https://your-app-name.railway.app`

## 🔐 Default Login Credentials
- **Email**: admin@example.com
- **Password**: admin123
- **⚠️ Change these after deployment!**

## 📱 Features Available Online:
- ✅ Hospital registration and management
- ✅ Donor and patient registration
- ✅ Smart matching system
- ✅ First-come-first-serve priority
- ✅ Unique ID system
- ✅ Real-time match notifications
- ✅ Responsive design for mobile
- ✅ Secure authentication

## 🚨 Troubleshooting

### Common Windows Issues:

**1. psycopg2 Installation Error**
- **Solution**: Skip psycopg2 for local development
- **Production**: Railway will install it automatically

**2. Unicode Encoding Errors**
- **Solution**: Use UTF-8 encoding in scripts
- **Fixed**: All deployment scripts now use UTF-8

**3. Git Not Found**
- **Solution**: Install Git for Windows
- **Download**: https://git-scm.com/download/win

**4. Python Not in PATH**
- **Solution**: Add Python to system PATH
- **Or**: Use full path to python.exe

### Getting Help:
- Check Railway logs in dashboard
- Verify environment variables
- Test locally first
- Check database connection

## 🎯 Next Steps:
1. **Run**: `python deploy_windows.py`
2. **Create**: GitHub repository
3. **Deploy**: To Railway
4. **Test**: Your live app
5. **Share**: With hospitals!

## 💡 Pro Tips:
- **Start with free tiers** to test
- **Use strong secret keys**
- **Test locally** before deploying
- **Monitor your app** after deployment
- **Keep backups** of your database

---

**Your Organ Donor Chain will be live on the internet! 🌐**
