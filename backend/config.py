import os 

OPENAI_API_BASE_URL = os.getenv('OPENAI_API_BASE_URL', None)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'EMPTY')
ADMIN_USER_EMAIL = os.getenv('ADMIN_USER_EMAIL', "")
ADMIN_USER_PASSWORD = os.getenv('ADMIN_USER_PASSWORD', "")


HOST = os.getenv('HOST', None)
PORT = os.getenv('PORT', None)
