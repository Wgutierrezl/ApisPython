from pydantic import BaseModel
from datetime import date

class Usuarios(BaseModel):
    id_usuario:str
    nombre:str
    correo:str
    contrasena:str
    tipo:str
    fecha_registro:date