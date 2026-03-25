import allure
import pytest

from config.config import settings


@allure.epic("Booking API")
@allure.feature("Authentication")
class TestAuthentication:
    """Tests for POST /auth endpoint."""

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Valid credentials return a token")
    @pytest.mark.smoke
    def test_auth_valid_credentials(self, auth_client):
        """Verify that valid credentials return a valid token."""
        token = auth_client.create_token(
            settings.AUTH_USERNAME, settings.AUTH_PASSWORD
        )
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Invalid credentials do not return a token")
    @pytest.mark.parametrize(
        "username,password",
        [
            pytest.param("wrong_user", "wrong_pass", id="invalid-both"),
            pytest.param(settings.AUTH_USERNAME, "wrong_pass", id="invalid-password"),
            pytest.param("wrong_user", settings.AUTH_PASSWORD, id="invalid-username"),
        ],
    )
    @pytest.mark.regression
    def test_auth_invalid_credentials(self, auth_client, username, password):
        """Verify that invalid credentials do not return a token."""
        response = auth_client.create_token_raw(username, password)
        assert response.status_code == 200
        data = response.json()
        assert "token" not in data, f"Token should not be returned for invalid credentials: {data}"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Empty credentials do not return a token")
    @pytest.mark.parametrize(
        "username,password",
        [
            pytest.param("", "", id="both-empty"),
            pytest.param("", settings.AUTH_PASSWORD, id="empty-username"),
            pytest.param(settings.AUTH_USERNAME, "", id="empty-password"),
        ],
    )
    @pytest.mark.negative
    def test_auth_empty_credentials(self, auth_client, username, password):
        """Verify that empty credentials do not return a token."""
        response = auth_client.create_token_raw(username, password)
        assert response.status_code == 200
        data = response.json()
        assert "token" not in data, f"Token should not be returned for empty credentials: {data}"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Token format is a non-empty string")
    @pytest.mark.regression
    def test_auth_token_format(self, auth_client):
        """Verify that the returned token is a non-empty string of reasonable length."""
        token = auth_client.create_token(
            settings.AUTH_USERNAME, settings.AUTH_PASSWORD
        )
        assert isinstance(token, str)
        assert len(token) > 5, "Token should be at least 5 characters"
