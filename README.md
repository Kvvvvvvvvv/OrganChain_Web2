# Organ Donation Management System

A web-based system for managing organ donations and patient matching across hospitals.

## Project Structure

```
├── client/                 # Frontend files
│   ├── static/            # CSS, JS, images
│   ├── templates/         # HTML templates
│   ├── ui_demo.html       # UI demo page
│   └── UI_DEMO_README.md  # UI documentation
├── server/                # Backend files
│   ├── app.py            # Flask application
│   ├── database.db       # SQLite database
│   ├── requirements.txt  # Python dependencies
│   ├── create_gifs.py    # Utility scripts
│   └── view_database.py  # Database viewer
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile            # Docker configuration
└── README.md             # This file
```

## Features

- **Admin Panel**: Manage hospitals, view all donors/patients, track matches
- **Hospital Dashboard**: Add donors/patients, view matches, manage records
- **Organ Matching**: Automatic matching based on organ type and blood type
- **FCFS System**: First-Come-First-Served matching with unique IDs
- **Secure Authentication**: Role-based access (Admin/Hospital)

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository
2. Run the application:
   ```bash
   docker-compose up -d
   ```
3. Access the application at `http://localhost:5000`

### Manual Setup

1. **Backend Setup**:
   ```bash
   cd server
   pip install -r requirements.txt
   python app.py
   ```

2. **Access the application**:
   - URL: `http://localhost:5000`
   - Default Admin: `admin@gmail.com` / `1234`

## Default Credentials

- **Admin**: 
  - Email: `admin@gmail.com`
  - Password: `1234`

## API Endpoints

### Authentication
- `GET/POST /login` - Login page
- `GET /logout` - Logout

### Admin Routes
- `GET /manage_hospitals` - Manage hospitals
- `GET /admin_donors` - View all donors
- `GET /admin_patients` - View all patients
- `GET /admin_matches` - View all matches
- `GET/POST /add_hospital` - Add new hospital

### Hospital Routes
- `GET /hospital_dashboard` - Hospital dashboard
- `GET /hospital_donors` - View hospital donors
- `GET /hospital_patients` - View hospital patients
- `GET /hospital_matches` - View hospital matches
- `GET/POST /add_donor` - Add new donor
- `GET/POST /add_patient` - Add new patient

### Matching
- `GET /matches` - View and process matches
- `GET /match_records` - View match history

## Database Schema

- **admin**: Admin users
- **hospital**: Hospital information
- **donor**: Donor records with unique IDs
- **patient**: Patient records with unique IDs
- **match_record**: Successful matches

## Deployment

### Production Deployment

1. **Using Docker**:
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

2. **Environment Variables**:
   - `FLASK_ENV=production`
   - `FLASK_APP=app.py`

3. **Database**: The SQLite database is persisted in a volume

### Cloud Deployment

The application is ready for deployment on:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Heroku
- DigitalOcean App Platform

## Development

### Adding New Features

1. Backend changes go in `server/`
2. Frontend changes go in `client/`
3. Update templates in `client/templates/`
4. Update static files in `client/static/`

### Database Management

- View database: `python server/view_database.py`
- Database file: `server/database.db`

## Security Notes

- Change default admin credentials in production
- Use environment variables for sensitive data
- Consider using PostgreSQL for production
- Implement proper session management
- Add HTTPS in production

## Support

For issues or questions, please check the documentation or create an issue in the repository.
