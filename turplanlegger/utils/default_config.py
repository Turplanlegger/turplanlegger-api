# App
TOKEN_EXPIRE_TIME = 86400  # Seconds

# Database
DATABASE_URI = """postgresql://postgres:postgres@localhost/turplanlegger
                ?connect_timeout=10&application_name=turplanlegger"""
DATABASE_NAME = 'turplanlegger'

# Logging
LOG_TO_FILE = False

# Misc
CREATE_ADMIN_USER = False

# CORS
CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'Access-Control-Allow-Origin', 'X-Request-ID']
CORS_ORIGINS = ['http://localhost:3000']
CORS_SUPPORTS_CREDENTIALS = True

SECRET_KEY = 'tVKUtcx_n9rt5afY_2WFNvU6PlFMggCatsZ3l4RjKxH0jgdLq6CScb0P3ZGXYbPzXvmmLiWZizpb-h0qup5jznOvOr-Dhw9908584BSgC83YacjWNqEK3urxhyE2jWjwRm2N95WGgb5mzE5XmZIvkvyXnn7X8dvgFPF5QwIngGsDG8LyHuJWlaDhr_EPLMW4wHvH0zZCuRMARIJmmqiMy3VD4ftq4nS5s8vJL0pVSrkuNojtokp84AtkADCDU_BUhrc2sIgfnvZ03koCQRoZmWiHu86SuJZYkDFstVTVSR0hiXudFlfQ2rOhPlpObmku68lXw-7V-P7jwrQRFfQVXw'
