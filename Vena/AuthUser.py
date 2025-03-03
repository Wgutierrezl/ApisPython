from sqlmodel import Session,select
from ModelSQL.Usuarios import User

async def GetUser(sesion:Session,email:str):
    try:
        statement=select(User).where(User.correo==email)
        result=sesion.exec(statement)
        return result.first()
            
    except Exception as e:
        print(str(e))