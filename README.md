# LMS_backend

# First Time Project Setup
## Requirements/Versions
- Python 3.9.x (3.9.13)
- pipenv 2023.8.28 or virtualenv 20.24.4

#### Add Environment Variables to Your Project
In your project, create or update your `.env` file:
```dotenv
DB_HOST='your db host'
DB_NAME='your database'
DB_USER='user name'
DB_PASSWORD='your password'
```
This will setup the database

## Web Server
- Setup virtual environment `virtualenv venv` and **activate it**
- Install dependencies `pip install -r requirements.txt`

### More Database
1. Make Database Migrations
    ```bash
    python manage.py makemigrations
    ```
2. Migrate Database
    ```bash
    python manage.py migrate
    ```
3. Setup a Super User
    ```bash
    python manage.py createsuperuser
    ```
### Run Server
`python manage.py runserver`