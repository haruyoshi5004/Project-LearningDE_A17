from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError
import jwt

from setup import jsonLoad

if TYPE_CHECKING:
    from schemas import User, UserSql

SECRETKEY: str = jsonLoad(Path("configs/secrets.json"))["secretKey"]  # type:ignore
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")
password_hash = PasswordHash.recommended()


def AuthUser(email: str, password: str) -> bool:
    from schemas import UserSql

    user = UserSql.getOne(email)
    if user is None:
        return False
    # return True only when the hashed password matches
    return verifyPassword(password, user.hashedPassword)


def getCurrentUser(token: str = Depends(oauth2_scheme)) -> "User | None":
    user = decodeToken(token)
    # return user
    if user is None:
        # 401 Unauthorized when token is invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return user.asUser()


def verifyPassword(rawPassword: str, hashedPassword: str) -> bool:
    return password_hash.verify(rawPassword, hashedPassword)


def hashPassword(rawPassword: str) -> str:
    return password_hash.hash(rawPassword)


def generateToken(email: str) -> str:
    """Generate a JWT token with subject=email and expiration."""
    to_encode = {"sub": email, "iat": int(datetime.now(tz=timezone.utc).timestamp())}
    expire = datetime.now(tz=timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRETKEY, algorithm=ALGORITHM)


def decodeToken(token: str) -> "UserSql | None":
    from schemas import UserSql

    try:
        payload = jwt.decode(token, SECRETKEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except (InvalidTokenError, jwt.DecodeError):
        return None
    user = UserSql.getOne(email)
    return user
