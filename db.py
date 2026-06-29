import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    return SessionLocal()

def query(sql, params=None):
    for attempt in range(2):
        db = get_db()
        try:
            result = db.execute(text(sql), params or {})
            return [dict(r._mapping) for r in result.fetchall()]
        except OperationalError:
            if attempt == 0:
                time.sleep(2)
            else:
                raise
        finally:
            db.close()
