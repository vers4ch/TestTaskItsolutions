from sqlalchemy import Column, Integer, String
from database import Base

class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    ad_id = Column(Integer, unique=True, index=True, nullable=False)
    author = Column(String, index=True)
    views = Column(Integer, index=True)
    position = Column(Integer, index=True)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
