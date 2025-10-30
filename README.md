# Mumbai Smart City Platform

A comprehensive Django-based platform for smart city management, featuring citizen complaint tracking, emergency SOS services, infrastructure monitoring, and more.

## Features

- **User Management**: Secure authentication with Google OAuth2 integration
- **Complaint System**: Citizens can report and track infrastructure issues
- **Emergency SOS**: Real-time emergency request system with AI-powered assistance
- **Discussion Forum**: Community discussions and civic engagement
- **Logistics Dashboard**: Infrastructure project tracking and monitoring
- **Arduino Integration**: IoT smoke sensor monitoring with real-time alerts
- **Weather Information**: Weather updates and alerts
- **Manager Portal**: Administrative dashboard for complaint management

## Technology Stack

- **Backend**: Django 5.0.7
- **AI Integration**: Google Gemini AI for intelligent suggestions
- **Authentication**: Social Auth (Google OAuth2)
- **Database**: SQLite (development) / PostgreSQL (production)
- **IoT**: Arduino with serial communication
- **APIs**: Google Maps, Weather APIs, IRCTC

## Installation

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd project
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your credentials:
```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
GEMINI_API_KEY=your_gemini_api_key
OPENROUTE_API_KEY=your_openroute_api_key
ARDUINO_COM_PORT=COM3
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

8. Access the application at `http://localhost:8000`

## Project Structure

```
project/
├── users/              # User authentication and profiles
├── sos/                # Emergency SOS system
├── discussion/         # Discussion forum
├── logistics/          # Infrastructure monitoring
├── arduinofeature/     # IoT smoke sensor integration
├── weather/            # Weather information
├── manager/            # Admin management portal
├── utils/              # Utility functions and caching
├── project/            # Main project settings
├── media/              # User uploaded files
└── requirements.txt    # Project dependencies
```

## Key Features Explained

### Complaint Management
- Users can submit complaints with images and locations
- AI-powered categorization and priority assignment
- Real-time status tracking
- Email notifications on status updates

### Emergency SOS
- One-click emergency request
- AI-powered emergency response suggestions
- Geolocation-based service routing
- Multiple emergency categories support

### Arduino Smoke Monitoring
- Real-time smoke level monitoring
- Configurable alert thresholds
- Historical data visualization
- AI-powered air quality suggestions

### Infrastructure Monitoring
- Track Mumbai infrastructure projects
- Metro construction updates
- Road development plans
- Project bottleneck analysis

## API Rate Limits

**Note**: The IRCTC API endpoints may have rate limits:
- Status code 401: Invalid or unauthorized API key
- Status code 429: Rate limit exceeded

Ensure you have valid API credentials and monitor your usage.

## Deployment

For production deployment:

1. Update `settings.py`:
   - Set `DEBUG = False`
   - Configure `ALLOWED_HOSTS`
   - Use PostgreSQL database
   - Configure static file serving

2. Use Gunicorn as WSGI server:
```bash
gunicorn project.wsgi:application
```

3. Set up proper environment variables
4. Configure reverse proxy (nginx/Apache)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Contact

Project Link: [https://github.com/yourusername/your-repo-name](https://github.com/yourusername/your-repo-name)

## Acknowledgments

- Google Gemini AI for intelligent features
- OpenRouteService for mapping
- Django community for excellent documentation
