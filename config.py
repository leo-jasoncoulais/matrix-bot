import json
import os
from dotenv import load_dotenv

load_dotenv()

HOMESERVER = "https://"+os.getenv('HOMESERVER')
USER_ID = f"@{os.getenv('USER_ID')}:{os.getenv('HOMESERVER')}"
PASSWORD = os.getenv('PASSWORD')
DEVICE_NAME = os.getenv('USER_ID')
CREDENTIALS_FILE = "credentials.json"
STORE_PATH = "./store"
ADMIN_FILE="admins.json"

if os.path.exists(ADMIN_FILE):
    with open("admins.json") as f:
        ADMINS = set(json.load(f))
else:
    ADMINS = []