from sqlalchemy.orm import Session
from database.models import User
from schema import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class Crud:

    @staticmethod
    def get_user(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create_user(
        db: Session, user: UserCreate, refresh_token: str, access_token: str
    ):
        hashed_password = pwd_context.hash(user.password)
        db_user = User(
            username=user.username,
            password=hashed_password,
            refresh_token=refresh_token,
            access_token=access_token,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user_tokens(
        db: Session, user_id: int, access_token: str, refresh_token: str
    ):
        user = Crud.get_user(db, user_id)
        if user:
            user.access_token = access_token
            user.refresh_token = refresh_token
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = Crud.get_user(db, user_id)
        if user:
            db.delete(user)
            db.commit()
        return user
