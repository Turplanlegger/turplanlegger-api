# App
TOKEN_EXPIRE_TIME = 86400  # Seconds

# Database
DATABASE_URI = """postgresql://postgres:postgres@localhost/turplanlegger
                ?connect_timeout=10&application_name=turplanlegger"""
DATABASE_NAME = 'turplanlegger'

# Logging
LOG_LEVEL = 'INFO'
LOG_TO_FILE = False
LOG_PATH = '/var/log/turplanlegger.log'

# Misc
CREATE_ADMIN_USER = False

# CORS
CORS_ORIGINS = ['http://localhost:3000']

# Auth
AUDIENCE = '0149fc65-259e-4895-9034-e144c242f733'
AZURE_AD_B2C_KEY_URL = ('https://turplanlegger.b2clogin.com/'
                        'turplanlegger.onmicrosoft.com/discovery/'
                        'v2.0/keys?p=b2c_1_signin')
