from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .database import Base, engine, get_db
from .models import User, Project, Task, Comment

Base.metadata.create_all(bind=engine)
app = FastAPI()

class UserCreate(BaseModel):
    FullName: str
    Email: str
    PasswordHash: str

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.Email == user.Email).first()
    if existing:
        raise HTTPException(400, "User already exists")
    new_user = User(FullName=user.FullName, Email=user.Email, PasswordHash=user.PasswordHash)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"UserID": new_user.UserID, "FullName": new_user.FullName}

@app.get("/projects/")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [{"ProjectID": p.ProjectID, "ProjectName": p.ProjectName} for p in projects]
