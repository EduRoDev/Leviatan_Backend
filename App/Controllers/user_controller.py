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




@router.get("/data", response_model=UserDataResponse)
def userData(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(current_user["id"])
    return UserDataResponse(
        name=user.name,
        last_name=user.last_name,
        email=user.email
    )

@router.put("/edit")
def editUser(request: UserEditRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    auth_service = AuthService(db)
    try:
        Id = current_user["id"]
        user = auth_service.editUser(Id, request.name, request.last_name, request.email)
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
        
@router.put("/change_password")
def change_password(request: PasswordChangeRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    auth_service = AuthService(db)
    try:
        Id = current_user["id"]
        auth_service.change_password(Id, request.old_password, request.new_password)
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))