def test_swagger_docs_csp_allows_required_assets(client):
    response = client.get("/docs")

    assert response.status_code == 200
    csp = response.headers["content-security-policy"]
    assert "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net" in csp
    assert "connect-src 'self' https://cdn.jsdelivr.net" in csp


def test_api_csp_remains_restrictive(client):
    response = client.get("/api/v1/auth/login")

    assert response.status_code == 405
    assert response.headers["content-security-policy"] == (
        "default-src 'none'; frame-ancestors 'none'"
    )
