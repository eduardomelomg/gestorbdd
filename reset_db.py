from app import create_app
from app.extensions import db
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    
    print("Creating fresh admin user...")
    admin = Usuario(nome="Eduardo", email="admin@test.com", role="Admin")
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()
    print("Database reset complete. Admin: admin@test.com / admin123")
