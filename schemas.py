from pydantic import BaseModel

# Existing Ad schema
class Ad(BaseModel):
    id: int
    title: str
    ad_id: int
    author: str
    views: int
    position: int

    class Config:
        orm_mode = True

# New User schema for registration
class UserCreate(BaseModel):
    username: str
    password: str

# New User schema for response
class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str
