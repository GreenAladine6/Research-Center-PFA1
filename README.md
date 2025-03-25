# Chawarma ya hala

Chawarma ya hala is a web application built with Flask, providing a dashboard and API for managing designer-related services, portfolios, and team information.

## Features

- User authentication and login system
- Dashboard for managing:
  - Orders
  - Menu
- RESTful API for programmatic access
- Responsive design with static assets

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd Designers-Junior-Entreprise
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env`:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

## Running the Application

1. Start the development server:
```bash
flask run
```

2. Access the application at `http://localhost:5000`

## Deployment

For production, use a WSGI server like Gunicorn:
```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a Pull Request
