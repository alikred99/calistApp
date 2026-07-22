import bcrypt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import jwt
import os


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def hashear_password(password: str):
    hash_generado = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hash_generado.decode('utf-8')
def verificar_password(password: str, hash_guardado):
    return bcrypt.checkpw(password.encode('utf-8'), hash_guardado.encode('utf-8'))

def crear_token(datos: dict):
    datos_copia = datos.copy()
    expiracion = datetime.now(timezone.utc) + timedelta(hours=2)
    datos_copia.update({"exp": expiracion})
    token = jwt.encode(datos_copia, SECRET_KEY, algorithm=ALGORITHM)
    return token
def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # paylaod = informacion por ejemplo "sub": 3,"exp"
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    payload = verificar_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado"
        )
    return payload
