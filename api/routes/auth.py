from fastapi import APIRouter, Depends, HTTPException, status
from core.crud import Crud
from sqlalchemy.orm import Session
from schema import TokenResponse, UserLogin, UserResponse, UserCreate
from core.database import get_db
from core.hash import create_access_token, create_refresh_token
from core.config import config
import jwt

router = APIRouter(prefix="/auth")


@router.post(
    "/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = Crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    return Crud.create_user(db=db, user=user)


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = Crud.get_user_by_username(db, username=user.username)
    if not db_user or not Crud.pwd_context.verify(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"sub": db_user.username})
    refresh_token = create_refresh_token(data={"sub": db_user.username})

    Crud.update_user_tokens(db, db_user.id, access_token, refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.get("/me", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = Crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/refresh/", response_model=TokenResponse)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            refresh_token, config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    db_user = Crud.get_user_by_username(db, username=username)
    if db_user is None or db_user.refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Generate new tokens
    new_access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})

    Crud.update_user_tokens(db, db_user.id, new_access_token, new_refresh_token)

    return {"access_token": new_access_token, "refresh_token": new_refresh_token}
