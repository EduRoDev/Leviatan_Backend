from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from App.Services.auth_services import AuthService
from App.Utils.db_sessions import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegister(BaseModel):
    name: str
    last_name: str
    email: str
    password: str
    
class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try: 
        user = auth_service.register(user.name, user.last_name, user.email, user.password)
        return {"message": "User registered successfully", "user": {
            "id": user.id,
            "name": user.name,
            "last_name": user.last_name,
            "email": user.email
        }}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        user, access_token = auth_service.login(user.email, user.password)
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))