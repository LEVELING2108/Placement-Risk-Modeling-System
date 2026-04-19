from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core import security
from app.api.deps import USERS_DB

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)
    # Note: In a real app, use security.verify_password. 
    # For demo, I'll just check if it matches "password123"
    if not user or form_data.password != "password123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(
        data={"sub": user["username"], "tenant_id": user["tenant_id"]}
    )
    return {"access_token": access_token, "token_type": "bearer", "tenant_id": user["tenant_id"]}
