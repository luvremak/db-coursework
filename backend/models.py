from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, TIMESTAMP
from .db import Base

class User(Base):
    __tablename__ = "User"
    UserID = Column(Integer, primary_key=True)
    FullName = Column(String(100), nullable=False)
    Email = Column(String(100), nullable=False, unique=True)
    PasswordHash = Column(String(255), nullable=False)

class Project(Base):
    __tablename__ = "Project"
    ProjectID = Column(Integer, primary_key=True)
    ProjectName = Column(String(100), nullable=False)
    Description = Column(Text)
    StartDate = Column(Date, nullable=False)
    EndDate = Column(Date)
    TeamID = Column(Integer, ForeignKey("Team.TeamID", ondelete="SET NULL"))

class Task(Base):
    __tablename__ = "Task"
    TaskID = Column(Integer, primary_key=True)
    Title = Column(String(150), nullable=False)
    Description = Column(Text)
    Status = Column(String(50), default="To Do")
    Priority = Column(String(20))
    DueDate = Column(Date)
    BoardID = Column(Integer, ForeignKey("Board.BoardID", ondelete="CASCADE"))

class Comment(Base):
    __tablename__ = "Comment"
    CommentID = Column(Integer, primary_key=True)
    Content = Column(Text, nullable=False)
    CreatedAt = Column(TIMESTAMP)
    UserID = Column(Integer, ForeignKey("User.UserID", ondelete="CASCADE"))
    TaskID = Column(Integer, ForeignKey("Task.TaskID", ondelete="CASCADE"))
