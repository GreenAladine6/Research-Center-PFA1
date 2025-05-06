# Reaserch-center
To be able to run ower the website you need to :
  -Download the requirements shown in description below

    . Install dependencies:
    ```bash
    pip install -r requirements.txt


  -Next you should run the command:
  ``` bash
   py app.py
   
   python app.py

   ```


  -For login Admin:
    loginadmin@gmail.com
    password: adminadmin

  -For Researcher (User) login try :
    william.davis481@science.net
    password: researcher123

  or try any researcher email from data.json using the same password researcher123


## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd RESEARCH-CENTER-PFA1
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

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
