from sqlalchemy.orm import Session
from App.Models.models import User
from App.Utils.auth_utils import hash_password, verify_password, create_access_token

class AuthService():
    def __init__(self, db: Session):
        self.db = db
        
    def login(self, email: str, password: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password):
            raise ValueError("Invalid email or password")
        
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        return user, access_token
    
    def register(self, name: str, last_name: str, email: str, password: str) -> User:
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        new_user = User(name=name,
                        last_name=last_name,
                        email=email,
                        password=hash_password(password))
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
    
    def editUser(self, user_id: int, name: str, last_name: str, email: str) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.name = name
        user.last_name = last_name
        user.email = email
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        if not verify_password(old_password, user.password):
            raise ValueError("Old password is incorrect")
        
        if old_password == new_password:
            raise ValueError("New password must be different from the old password")
        
        if len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters long")
        
        user.password = hash_password(new_password)
        self.db.commit()
        
    def get_user_by_id(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        return user
    
    