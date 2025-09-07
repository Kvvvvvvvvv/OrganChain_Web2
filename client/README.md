# Organ Donation Management System - Frontend

This is the frontend/client portion of the Organ Donation Management System, designed to be deployed as a static site on Vercel.

## 🚀 Deployment on Vercel

### Quick Deploy
1. Go to [Vercel](https://vercel.com)
2. Import your GitHub repository
3. **Set Root Directory to `client`**
4. Deploy!

### Vercel Settings
- **Framework Preset**: `Other`
- **Root Directory**: `client`
- **Build Command**: Leave empty
- **Output Directory**: Leave empty

## 📁 Structure

```
client/
├── index.html              # Main landing page
├── static/                 # CSS and assets
│   └── style.css          # Main stylesheet
├── templates/              # HTML templates (for reference)
├── ui_demo.html           # UI demo page
├── vercel.json            # Vercel configuration
├── package.json           # Project configuration
└── README.md              # This file
```

## 🎨 Features

- **Responsive Design**: Works on all devices
- **Modern UI**: Beautiful gradient design
- **Smooth Animations**: CSS animations and transitions
- **Interactive Elements**: JavaScript for enhanced UX
- **Static Site**: No backend required for deployment

## 🔗 Pages

- **Home (`/`)**: Landing page with features and information
- **About (`/#about`)**: System features and capabilities
- **Login (`/#login`)**: Access information and demo credentials
- **Contact (`/#contact`)**: Contact information

## 🎯 Demo Credentials

**Admin Access:**
- Email: admin@gmail.com
- Password: 1234

**Note**: This is a frontend-only deployment. The full application with backend functionality requires the complete Flask application deployment.

## 🛠️ Local Development

```bash
# Navigate to client directory
cd client

# Start local server
python -m http.server 3000

# Or use Node.js
npx serve .

# Access at http://localhost:3000
```

## 📱 Responsive Design

The site is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🎨 Styling

- **CSS Custom Properties**: Modern CSS variables
- **Flexbox & Grid**: Modern layout techniques
- **Gradients**: Beautiful color schemes
- **Animations**: Smooth transitions and effects
- **Glass Morphism**: Modern UI effects
