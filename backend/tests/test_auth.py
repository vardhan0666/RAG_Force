import pytest


@pytest.mark.asyncio
async def test_register_and_login_user(client):
    # Test Register
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "researcher@ragforge.io", "password": "SecurePassword123!", "full_name": "AI Researcher"},
    )
    assert reg_response.status_code == 201
    data = reg_response.json()
    assert data["email"] == "researcher@ragforge.io"

    # Test Login
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "researcher@ragforge.io", "password": "SecurePassword123!"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"