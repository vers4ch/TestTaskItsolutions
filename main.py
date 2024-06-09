from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Ad as AdModel, User as UserModel
from schemas import Ad as AdSchema, UserCreate, User, Token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Объект для схемы OAuth2, который будет использоваться для получения токенов
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Контекст для работы с хешированием паролей, используем bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db  # Возвращаем сессию базы данных
    finally:
        db.close()  # Закрываем сессию после использования

# Функция для проверки пароля
# plain_password - пароль, введенный пользователем
# hashed_password - захешированный пароль, хранящийся в базе данных
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Функция для хеширования пароля
# password - пароль, который необходимо захешировать
def get_password_hash(password):
    return pwd_context.hash(password)

# Функция для создания токена доступа
# data - данные, которые необходимо закодировать в токен
# expires_delta - время жизни токена
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()  # Создаем копию данных для кодирования
    if expires_delta:
        # Устанавливаем время истечения токена, если оно передано
        expire = datetime.utcnow() + expires_delta
    else:
        # Устанавливаем стандартное время истечения токена (15 минут)
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})  # Добавляем время истечения в данные для кодирования
    # Кодируем JWT токен с использованием секретного ключа и алгоритма
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Маршрут для регистрации нового пользователя
# user - данные пользователя, переданные в запросе
# db - сессия базы данных
@app.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        # Проверка на существование пользователя с таким же именем в базе данных
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)  # Хешируем пароль пользователя
    db_user = UserModel(username=user.username, hashed_password=hashed_password)
    db.add(db_user)  # Добавляем нового пользователя в сессию
    db.commit()  # Фиксируем изменения в базе данных
    db.refresh(db_user)  # Обновляем объект пользователя из базы данных
    return db_user

# Маршрут для получения токена доступа
# form_data - данные формы запроса, содержащие имя пользователя и пароль
# db - сессия базы данных
@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Проверка на корректность введенных данных пользователя
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Устанавливаем время истечения токена
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Маршрут для получения информации о конкретном объявлении
# ad_id - идентификатор объявления
# token - токен доступа
# db - сессия базы данных
@app.get("/ads/{ad_id}", response_model=AdSchema)
async def read_ad(ad_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Декодируем токен для получения данных
        username: str = payload.get("sub")
        if username is None:
            # Проверка токена на валидность (наличие имени пользователя)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    ad = db.query(AdModel).filter(AdModel.ad_id == ad_id).first()
    if ad is None:
        # Проверка на существование объявления с указанным ID
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad

# Маршрут для получения информации о текущем пользователе
# token - токен доступа
# db - сессия базы данных
@app.get("/users/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Декодируем токен для получения данных
        username: str = payload.get("sub")
        if username is None:
            # Проверка токена на валидность (наличие имени пользователя)
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user is None:
        raise credentials_exception  # Если пользователь не найден, вызываем исключение
    return user  # Возвращаем информацию о текущем пользователе
