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
        
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
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