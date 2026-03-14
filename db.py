import os

import psycopg2

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://hackathon:hackathon@localhost:5432/hackathon"
)

def get_db():
    return psycopg2.connect(DATABASE_URL)
