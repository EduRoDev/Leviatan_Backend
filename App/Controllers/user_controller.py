from App.Utils.auth_utils import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from App.Services.auth_services import AuthService
from App.Utils.db_sessions import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/user", tags=["user"])

class UserDataResponse(BaseModel):
    name: str
    last_name: str
    email: str

class UserEditRequest(BaseModel):
    name: str
    last_name: str
    email: str

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str




@router.get("/data/{user_id}", response_model=UserDataResponse)
def userData(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), user_id: int = None):
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id) 
    return UserDataResponse(
        name=user.name,
        last_name=user.last_name,
        email=user.email
    )

@router.put("/edit/{user_id}")
def editUser(request: UserEditRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), user_id: int = None):
    auth_service = AuthService(db)
    try:
        user = auth_service.editUser(user_id, request.name, request.last_name, request.email)
        return {
            "message": "User updated successfully",
            "user": {
                "name": user.name,
                "last_name": user.last_name,
                "email": user.email
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
@router.put("/change_password/{user_id}")
def change_password(request: PasswordChangeRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), user_id: int = None):
    auth_service = AuthService(db)
    try:
        auth_service.change_password(user_id, request.old_password, request.new_password)
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))