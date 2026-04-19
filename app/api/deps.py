from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Hardcoded users for demonstration
USERS_DB = {
    "lender_a": {
        "username": "lender_a",
        "hashed_password": "$2b$12$6uXySlyuS/E9O2eWf3uG/.5D7H3i6Q7.K1N3/1z9t9W9i9i9i9i9i", # "password123"
        "tenant_id": "tenant_a"
    },
    "lender_b": {
        "username": "lender_b",
        "hashed_password": "$2b$12$6uXySlyuS/E9O2eWf3uG/.5D7H3i6Q7.K1N3/1z9t9W9i9i9i9i9i", # "password123"
        "tenant_id": "tenant_b"
    }
}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = USERS_DB.get(username)
    if user is None:
        raise credentials_exception
    return user
