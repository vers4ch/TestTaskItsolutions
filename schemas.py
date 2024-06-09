from pydantic import BaseModel

# схема объявлений
class Ad(BaseModel):
    id: int
    title: str
    ad_id: int
    author: str
    views: int
    position: int

    class Config:
        orm_mode = True

# схема для создания аккаунта
class UserCreate(BaseModel):
    username: str
    password: str

# схема для ответа создания аккаунта
class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

# схема для ответа создания токена
class Token(BaseModel):
    access_token: str
    token_type: str
