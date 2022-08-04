#Config file
from os import getenv
from dotenv import load_dotenv
import json
load_dotenv()

MONGODB_SETTINGS = json.loads(getenv('MONGODB_SETTINGS', None))
JWT_SECRET_KEY = getenv('JWT_SECRET_KEY', None)
