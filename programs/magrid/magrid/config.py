import os

MAGRID_DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),'magrid_db')
MAGRID_DB_PATH = os.getenv('MAGRID_DB', MAGRID_DB_PATH)