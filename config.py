import os
from dotenv import load_dotenv

load_dotenv()

USER=os.getenv('USER')
PASSWORD=os.getenv('PASSWORD')
HOST=os.getenv('HOST')
DATABASE=os.getenv('DATABASE')

# Variables de configuración server db replica
USER_REPLICA=os.getenv('USER_REPLICA')
PASSWORD_REPLICA=os.getenv('PASSWORD_REPLICA')
HOST_REPLICA=os.getenv('HOST_REPLICA')
DATABASE_REPLICA=os.getenv('DATABASE_REPLICA')

# Credenciales API Wordpress
USER_WORDPRESS=os.getenv('USER_WORDPRESS')
PASSWORD_WORDPRESS=os.getenv('PASSWORD_WORDPRESS')

 # credenciles api woocommerce
USER_WOOCOMMERCE=os.getenv('USER_WOOCOMMERCE')
PASSWORD_WOOCOMMERCE=os.getenv('PASSWORD_WOOCOMMERCE')
# Credenciales para la autenticación Basic Auth
USER_WOOCOMMERCE_NOTE=os.getenv('USER_WOOCOMMERCE_NOTE')
PASSWORD_WOOCOMMERCE_NOTE=os.getenv('PASSWORD_WOOCOMMERCE_NOTE')

# Tus credenciales de AWS
aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')

#aws endpoint
aws_endpoint_getseller_url=os.getenv('AWS_ENDPOINT_GETSELLER_URL')


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


WORDPRESS_BASE_URL = os.getenv('WORDPRESS_BASE_URL')

WHAPI_URL = os.getenv('WHAPI_URL')
WHAPI_TOKEN = os.getenv('WHAPI_TOKEN')

WATI_BASE_URL = os.getenv('WATI_BASE_URL')
WATI_TOKEN = os.getenv('WATI_TOKEN')

AWS_INSERTION_URL = os.getenv('AWS_INSERTION_URL')

BUCKET_NAME = os.getenv('BUCKET_NAME')