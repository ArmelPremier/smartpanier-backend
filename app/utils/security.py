from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Utilisateur
from app.config import (SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES,REFRESH_TOKEN_EXPIRE_DAYS)


# =========================
# 🔒 VALIDATION CONFIG
# =========================

if not SECRET_KEY:
    raise Exception("SECRET_KEY manquante dans .env")


# =========================
# 🔒 SECURITY SCHEME
# =========================

security = HTTPBearer()


# =========================
# 🔒 PASSWORD HASHING
# =========================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# =========================
# 🔑 CREATE JWT TOKEN
# =========================

def create_access_token(data: dict):
    payload = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# =========================
# 🔍 DECODE TOKEN
# =========================

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
    
def verify_refresh_token(refresh_token: str):

    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Refresh token invalide"
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Refresh token expiré ou invalide"
        )


# =========================
# 👤 CURRENT USER
# =========================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        token_type = payload.get("type")

        if token_type != "access":
            raise HTTPException(
                status_code=401,
                detail="Access token requis"
            )

        email = payload.get("sub")

        if not email:
            raise HTTPException(
                status_code=401,
                detail="Token invalide"
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token invalide ou expiré"
        )

    user = db.query(Utilisateur).filter(
        Utilisateur.email_utilisateur == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Utilisateur introuvable"
        )

    return user

def create_refresh_token(data: dict):
    payload = data.copy()

    expire = datetime.utcnow() + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)