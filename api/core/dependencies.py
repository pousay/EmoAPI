# core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.config import config
from core.database import get_db
from core.crud import Crud
import jwt

bearer_scheme = HTTPBearer(auto_error=False)


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if not config.ENABLE_AUTH:
        return None  # allow through

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

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
        raise HTTPException(status_code=401, detail="Invalid token")

    return db_user
