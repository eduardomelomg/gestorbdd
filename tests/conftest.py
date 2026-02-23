import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """Application configured for testing against an in-memory SQLite DB."""
    app = create_app("default")
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
    })
    with app.app_context():
        _db.create_all()
        _seed_test_data()
        yield app
        _db.drop_all()


def _seed_test_data():
    """Minimal seed for tests."""
    from app.models.usuario import Usuario
    from app.models.cliente import Cliente
    from app.models.produto import Produto
    from app.models.insumo import Insumo
    from app.models.ficha_tecnica import FichaTecnica, FichaTecnicaItem

    admin = Usuario(nome="Admin Test", email="admin@test.com", role="Admin")
    admin.set_password("password")
    operador = Usuario(nome="Op Test", email="op@test.com", role="Operador")
    operador.set_password("password")
    _db.session.add_all([admin, operador])

    cliente = Cliente(nome="Cliente Teste", tipo="Pessoa", canal_preferencial="B2C",
                      tabela_preco="Varejo")
    _db.session.add(cliente)

    insumo = Insumo(nome="Chocolate Test", unidade="g",
                    quantidade_embalagem_compra=1000, preco_compra_embalagem=30.00,
                    estoque_atual=2000, estoque_minimo=100)
    _db.session.add(insumo)

    produto = Produto(nome="Brownie Test", sku="TEST-001", categoria="Brownie",
                      unidade_venda="un", preco_varejo=12.00, preco_atacado=9.00)
    _db.session.add(produto)
    _db.session.flush()

    ficha = FichaTecnica(produto_id=produto.id, rendimento_unidades=12,
                         mao_de_obra_total=10.00, perdas_percentual=5.0,
                         margem_desejada_percentual=60.0)
    _db.session.add(ficha)
    _db.session.flush()
    _db.session.add(FichaTecnicaItem(ficha_tecnica_id=ficha.id, insumo_id=insumo.id,
                                     quantidade_por_receita=200, tipo_item="Insumo"))
    _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Returns a test client already logged in as Admin."""
    client.post("/auth/login", data={"email": "admin@test.com", "password": "password"})
    return client
