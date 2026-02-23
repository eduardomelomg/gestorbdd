import os
from dotenv import load_dotenv
load_dotenv()

# Force SQLAlchemy to use postgresql://
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    os.environ["DATABASE_URL"] = db_url.replace("postgres://", "postgresql://", 1)

from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Verificando estrutura do banco no Supabase...")
    try:
        # Add column if not exists
        db.session.execute(text("ALTER TABLE insumos ADD COLUMN IF NOT EXISTS peso_por_embalagem NUMERIC(10, 4) DEFAULT 1"))
        db.session.commit()
        print("Coluna 'peso_por_embalagem' adicionada/verificada com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar banco: {e}")
        db.session.rollback()

print("Migração concluída! 🚀")
