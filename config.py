import os
from dotenv import load_dotenv

load_dotenv()

HOMESERVER = "https://"+os.getenv('HOMESERVER')
USER_ID = f"@{os.getenv('USER_ID')}:{os.getenv('HOMESERVER')}"
PASSWORD = os.getenv('PASSWORD')
DEVICE_NAME = os.getenv('USER_ID')
CREDENTIALS_FILE = "credentials.json"
STORE_PATH = "./store"
NOTIFY_ROOM = os.getenv('NOTIFY_ROOM')