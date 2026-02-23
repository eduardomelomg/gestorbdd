import os
from dotenv import load_dotenv
load_dotenv()

# Force SQLAlchemy to use postgresql:// for the init script
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    os.environ["DATABASE_URL"] = db_url.replace("postgres://", "postgresql://", 1)

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    print("Conectando ao Supabase para criar tabelas...")
    db.create_all()
    print("Tabelas criadas com sucesso!")
    
    # Check if admin exists
    admin = Usuario.query.filter_by(role='Admin').first()
    if not admin:
        print("Criando usuário admin inicial...")
        admin = Usuario(
            nome="Eduardo", 
            email="browniedodudupnz@gmail.com", 
            role="Admin"
        )
        admin.set_password("Jampa*2021")
        db.session.add(admin)
        db.session.commit()
        print("Admin criado!")
    else:
        print("Admin já existe no Supabase.")

print("Deploy do banco concluído! 🚀")
