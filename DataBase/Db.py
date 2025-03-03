from sqlalchemy import create_engine

DATABASE_URL = "mysql+pymysql://root:wgutierrez2005@localhost:3306/TiendaDB?charset=utf8mb4"
engine = create_engine(DATABASE_URL)

try:
    conn = engine.connect()
    print("Conexión exitosa a la base de datos")  # ✅ Mensaje de éxito
    conn.close()
except Exception as e:
    print(f"Error al conectar con la base de datos: {e}")  # ✅ Mensaje de error