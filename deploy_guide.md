# 🌐 Deploy Organ Donor Chain to Internet

This guide will help you deploy your Flask application to the internet so everyone can access it with the database.

## 🚀 Deployment Options

### Option 1: Railway (Recommended - Free & Easy)
- **Free tier**: $5 credit monthly
- **Automatic deployments** from GitHub
- **Built-in database** support
- **Custom domains** available

### Option 2: Render (Free Tier Available)
- **Free tier**: 750 hours/month
- **Automatic SSL** certificates
- **PostgreSQL** database included
- **Easy GitHub integration**

### Option 3: Heroku (Paid but Reliable)
- **Paid service**: $7/month minimum
- **PostgreSQL** addon
- **Professional features**
- **High reliability**

## 📋 Pre-Deployment Checklist

### 1. Update Requirements
Make sure your `requirements.txt` includes all dependencies:

```txt
Flask==2.3.3
Werkzeug==2.3.7
```

### 2. Environment Variables
Create a `.env` file for sensitive data:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
```

### 3. Update App Configuration
Modify `app.py` for production:

```python
import os
from flask import Flask

app = Flask(__name__)

# Production configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL')
else:
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['DATABASE_URL'] = 'sqlite:///database.db'
```

## 🚀 Railway Deployment (Step-by-Step)

### Step 1: Prepare Your Code
1. **Create a GitHub repository**
2. **Upload your code** to GitHub
3. **Ensure all files** are committed

### Step 2: Set Up Railway
1. **Go to**: [railway.app](https://railway.app)
2. **Sign up** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository**

### Step 3: Configure Environment
1. **Go to Variables tab**
2. **Add these variables**:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-random-secret-key
   PORT=8000
   ```

### Step 4: Add Database
1. **Click "New" → "Database"**
2. **Select "PostgreSQL"**
3. **Railway will provide** `DATABASE_URL`
4. **Add to environment variables**

### Step 5: Deploy
1. **Railway will automatically deploy**
2. **Check logs** for any errors
3. **Your app will be live** at `https://your-app-name.railway.app`

## 🚀 Render Deployment (Step-by-Step)

### Step 1: Prepare Your Code
1. **Create a GitHub repository**
2. **Upload your code** to GitHub

### Step 2: Set Up Render
1. **Go to**: [render.com](https://render.com)
2. **Sign up** with GitHub
3. **Click "New" → "Web Service"**
4. **Connect your repository**

### Step 3: Configure Service
1. **Name**: `organ-donor-chain`
2. **Environment**: `Python 3`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python app.py`

### Step 4: Add Database
1. **Click "New" → "PostgreSQL"**
2. **Name**: `organ-donor-db`
3. **Render will provide** connection details

### Step 5: Environment Variables
Add these in Render dashboard:
```
FLASK_ENV=production
SECRET_KEY=your-random-secret-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

## 🔧 Database Migration (SQLite → PostgreSQL)

### Step 1: Install PostgreSQL Adapter
Add to `requirements.txt`:
```txt
Flask==2.3.3
Werkzeug==2.3.7
psycopg2-binary==2.9.7
```

### Step 2: Update Database Connection
Modify `app.py`:

```python
import os
import sqlite3
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    if os.environ.get('FLASK_ENV') == 'production':
        # PostgreSQL for production
        url = urlparse(os.environ.get('DATABASE_URL'))
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    else:
        # SQLite for development
        conn = sqlite3.connect('database.db')
    return conn
```

### Step 3: Update Database Schema
Create migration script:

```python
def migrate_to_postgresql():
    # Read SQLite data
    sqlite_conn = sqlite3.connect('database.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    postgres_conn = get_db_connection()
    postgres_cursor = postgres_conn.cursor()
    
    # Create tables in PostgreSQL
    postgres_cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Migrate data
    # ... (similar for other tables)
    
    postgres_conn.commit()
    postgres_conn.close()
    sqlite_conn.close()
```

## 🌐 Custom Domain Setup

### Step 1: Buy a Domain
- **Namecheap**: $8-15/year
- **GoDaddy**: $10-20/year
- **Google Domains**: $12/year

### Step 2: Configure DNS
1. **Go to your domain registrar**
2. **Add CNAME record**:
   ```
   Type: CNAME
   Name: www
   Value: your-app-name.railway.app
   ```

### Step 3: Add to Railway/Render
1. **Go to your app settings**
2. **Add custom domain**
3. **SSL certificate** will be auto-generated

## 🔒 Security Considerations

### 1. Environment Variables
- **Never commit** `.env` files
- **Use strong** secret keys
- **Rotate keys** regularly

### 2. Database Security
- **Use connection pooling**
- **Enable SSL** for database
- **Regular backups**

### 3. Application Security
- **Enable HTTPS** only
- **Set secure headers**
- **Rate limiting**

## 📊 Monitoring & Maintenance

### 1. Logs
- **Railway**: Built-in logging
- **Render**: Logs in dashboard
- **Monitor errors** regularly

### 2. Performance
- **Database indexing**
- **Query optimization**
- **Caching strategies**

### 3. Backups
- **Automated backups**
- **Test restore** procedures
- **Document recovery** process

## 🚨 Troubleshooting

### Common Issues:

**1. Database Connection Errors**
```python
# Check DATABASE_URL format
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

**2. Import Errors**
```bash
# Ensure all dependencies in requirements.txt
pip freeze > requirements.txt
```

**3. Port Issues**
```python
# Use environment PORT
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

**4. Static Files**
```python
# Ensure static files are served
app = Flask(__name__, static_folder='static')
```

## 📱 Mobile Optimization

### 1. Responsive Design
- **Test on mobile** devices
- **Optimize images**
- **Touch-friendly** buttons

### 2. Performance
- **Minimize CSS/JS**
- **Compress images**
- **Use CDN** for assets

## 🎯 Next Steps

1. **Choose deployment platform**
2. **Set up database**
3. **Configure environment**
4. **Deploy application**
5. **Test thoroughly**
6. **Set up monitoring**
7. **Configure custom domain**

## 💡 Pro Tips

- **Start with free tiers** to test
- **Use staging environment** for testing
- **Automate deployments** with GitHub
- **Monitor performance** regularly
- **Keep backups** of database
- **Document everything**

---

**Your Organ Donor Chain will be live on the internet! 🌐**
