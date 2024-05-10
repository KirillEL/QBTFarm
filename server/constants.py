import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().absolute().parent

POSTGRES_SCHEMAS_DIR = BASE_DIR / 'postgres_schemas'

SCHEMA_PATH = POSTGRES_SCHEMAS_DIR / 'schema.sql'
POSTGRES_DSN = os.getenv('POSTGRES_DSN')
