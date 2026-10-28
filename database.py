
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

load_dotenv()

url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(url)

def testar_conexao():
    with engine.connect() as conexao:
        resultado = conexao.execute(text("SELECT current_database()"))
        print(f"Conectado ao banco: {resultado.scalar()}")

if __name__ == "__main__":
    testar_conexao()

from models import Base

Base.metadata.create_all(bind=engine)