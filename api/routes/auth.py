from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.crud import Crud, pwd_context
from typing import Annotated
from sqlalchemy.orm import Session
from schema import TokenResponse, UserLogin, UserResponse, UserCreate
from core.database import get_db
from core.hash import create_access_token, create_refresh_token
from core.config import config
import jwt

router = APIRouter(prefix="/auth", tags=["AUTH"])
security = HTTPBearer()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = Crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return Crud.create_user(
        db=db, user=user, refresh_token=refresh_token, access_token=access_token
    )


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = Crud.get_user_by_username(db, username=user.username)
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"sub": db_user.username})
    refresh_token = create_refresh_token(data={"sub": db_user.username})

    Crud.update_user_tokens(db, db_user.id, access_token, refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.get("/me", response_model=UserResponse)
def read_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
):

    access_token = credentials.credentials
    try:
        payload = jwt.decode(
            access_token, config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    db_user = Crud.get_user_by_username(db, username=username)
    if db_user is None or db_user.access_token != access_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return db_user


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
):
    refresh_token = credentials.credentials
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

    new_access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})

    Crud.update_user_tokens(db, db_user.id, new_access_token, new_refresh_token)

    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


# TODO
# make this auth to be optional
