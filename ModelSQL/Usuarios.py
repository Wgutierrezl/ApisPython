from sqlmodel import SQLModel,Field
from datetime import date

class User(SQLModel,table=True):
    __tablename__="Usuarios"
    id_usuario:str=Field(default=None,primary_key=True)
    nombre:str=Field(default=None,unique=True)
    correo:str=Field(default=None,unique=True)
    contraseña:str=Field(default=None)
    tipo:str
    fecha_registro:date
    
    