import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_CREDS = {
    "username": os.getenv("ADMIN_USERNAME"),
    "password": os.getenv("ADMIN_PASSWORD")
}
BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")