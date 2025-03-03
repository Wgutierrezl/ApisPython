import jwt
from datetime import timedelta,timezone,datetime
from typing import Annotated
from fastapi import Depends,HTTPException,status,FastAPI
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session,select
from Vena.AuthUser import GetUser
from ModelToken.TokenClass import TokenData,Token
from ModelSQL.Usuarios import User
from BaseModel.Usuarios import Usuarios
from DataBase import Db


SECRET_KEY="b4f3a9c5d7e6f2a1849b3c0d5a7e8f6c2d1b4a3e9f8d7c6b0a5f2e3c1d8b9a7"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRES_MINUTES=30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

def get_session():
    with Session(Db.engine) as sesion:
        yield

def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def AuthenticaraUser(sesion:Session,email:str,password:str):
    statement=GetUser(sesion,email)
    if not statement:
        return None
    if not verify_password(password,statement.contraseña):
        return False
    return statement

def create_token_access(data:dict,expires_delta:timedelta | None = None):
    to_encode=data.copy()
    if expires_delta:
        expire=datetime.now(timezone.utc)+expires_delta
    else:
        expire=datetime.now(timezone.utc)+timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

async def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],sesion:Session=Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        correo=payload.get("sub")
        if correo is None:
            raise credentials_exception
        token_data=TokenData(correo=correo)
    except InvalidTokenError:
        raise credentials_exception
    user=GetUser(sesion,token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_currentt_user_activate(current_user:Annotated[User,Depends(get_current_user)]):
    if current_user.disable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Usuario inactivo")
    return current_user

@app.post("/Token",response_model=Usuarios)
async def Login(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],sesion:Session=Depends(get_session)) -> Token:
    try:
        user=AuthenticaraUser(sesion,form_data.username,form_data.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="email o contraseñas incorrectos")
        access_token_expire=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
        access_token=create_token_access(data={"sub":user.email},expires_delta=access_token_expire)
        return Token(access_token=access_token,token_type="Bearer")
        
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=(str(e)))

@app.get("/Users/me",response_model=User)
async def read_users_me(current_user:Annotated[User,Depends(get_currentt_user_activate)]):
    return current_user

@app.get("/Users/Me/item",response_model=User)
async def read_own_items(current_user:Annotated[User,Depends(get_currentt_user_activate)]):
    return {"UserID":current_user.id_usuario,
            "UserName":current_user.nombre,
            "Email":current_user.correo,
            "Contraseña":current_user.contraseña,
            "Tipo":current_user.tipo,
            "FechaRegistro":current_user.fecha_registro}
    
        
    