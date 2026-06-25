import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

_user = os.environ.get("USER", "simran")
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{_user}@/soccer?host=/var/run/postgresql")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    return SessionLocal()

def query(sql, params=None):
    db = get_db()
    try:
        result = db.execute(text(sql), params or {})
        return [dict(r._mapping) for r in result.fetchall()]
    finally:
        db.close()
