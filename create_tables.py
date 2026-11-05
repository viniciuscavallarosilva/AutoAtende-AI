
from database import Base, engine
import models

print("Criando tabelas no PostgreSQL...")

Base.metadata.create_all(bind=engine)

print("Tabelas criadas com sucesso!")
