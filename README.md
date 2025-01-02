# Backend

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/girishmahale786/backend.git
   ```

2. Navigate to the project directory:
    ```bash
    cd backend
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

4. Create an `.env` file in the project root and configure environment variables:
   ```bash
   SECRET_KEY='<your-secret-key>'
   DEBUG=True
   ALLOWED_HOSTS='*'
   SESSION_COOKIE_SECURE=False
   CSRF_COOKIE_SECURE=False
   CORS_ALLOW_CREDENTIALS=True
   CORS_ORIGIN_ALLOW_ALL=True
   CORS_ORIGIN_WHITELIST=''
   DATABASE_URL='psql://<user>:<password>@localhost:5432/<db_name>'
   SQLITE_URL='sqlite:///db.sqlite3'
   SITE_NAME='<your-site-name>'
   EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST='smtp.gmail.com'
   EMAIL_PORT=587
   EMAIL_HOST_USER='<your-email-address>'
   EMAIL_HOST_PASSWORD='<your-email-password>'
   EMAIL_USE_TLS=True
   EMAIL_USE_SSL=False
   SUPPORT_EMAIL='<your-support-email>'
   FRONTEND_CONFIRM_EMAIL_URL='<your-frontend-url>?key={key}'
   FRONTEND_PASSWORD_RESET_URL='<your-frontend-url>?uid={uid}&token={token}'
   GOOGLE_CALLBACK_URL='<your-google-callback-url>'

   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the project at:
   - API Docs (Swagger UI): `http://127.0.0.1:8000/docs/`
   - API Docs (Redoc UI): `http://127.0.0.1:8000/redoc/`
   - Admin Panel: `http://127.0.0.1:8000/admin/`


## Helpful Commands

### Install new packages
```bash
pip install package-name
pip freeze > requirements.txt
```

### Clear migrations
```bash
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
```