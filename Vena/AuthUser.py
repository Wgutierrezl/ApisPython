from sqlmodel import Session,select
from fastapi import HTTPException
from ModelSQL.Usuarios import User


def GetUser(sesion: Session, email: str):
    try:
        statement = select(User).where(User.correo == email)
        result = sesion.exec(statement).first()
        if not result:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return result
    except Exception as e:
        print(f"Error en GetUser: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en el servidor")