from database.database import SessionLocal, engine
from database.models import User

User.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
