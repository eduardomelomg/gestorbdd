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
        # Update existing columns to 2 decimal places
        alter_sql = """
        ALTER TABLE insumos 
          ALTER COLUMN quantidade_embalagem_compra TYPE NUMERIC(12, 2),
          ALTER COLUMN peso_por_embalagem TYPE NUMERIC(12, 2),
          ALTER COLUMN preco_compra_embalagem TYPE NUMERIC(12, 2),
          ALTER COLUMN estoque_atual TYPE NUMERIC(12, 2),
          ALTER COLUMN estoque_minimo TYPE NUMERIC(12, 2);
        """
        db.session.execute(text(alter_sql))
        db.session.commit()
        print("Precisão de decimais atualizada para (12, 2) com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar precisão: {e}")
        db.session.rollback()

print("Migração concluída! 🚀")
