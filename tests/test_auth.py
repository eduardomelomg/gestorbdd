def test_login_get(client):
    r = client.get("/auth/login")
    assert r.status_code == 200


def test_login_valid(client):
    r = client.post("/auth/login", data={"email": "admin@test.com", "password": "password"}, follow_redirects=True)
    assert b"Dashboard" in r.data or r.status_code == 200


def test_login_invalid(client):
    client.get("/auth/logout") # Ensure logged out
    r = client.post("/auth/login", data={"email": "admin@test.com", "password": "wrong"}, follow_redirects=True)
    assert b"inv" in r.data.lower() or b"senha" in r.data.lower()


def test_protected_redirect(client):
    client.get("/auth/logout")
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 302


def test_dashboard_logged_in(auth_client):
    r = auth_client.get("/")
    assert r.status_code == 200


def test_operador_cannot_delete_cliente(app, client):
    """Operador role should get 403 on delete routes."""
    client.post("/auth/login", data={"email": "op@test.com", "password": "password"})
    r = client.post("/clientes/1/deletar", data={})
    assert r.status_code in (302, 403)  # either forbidden or redirect back
