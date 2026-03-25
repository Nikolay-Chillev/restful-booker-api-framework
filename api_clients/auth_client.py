import allure

from api_clients.base_client import BaseClient
from models.auth_model import AuthResponse
from utils.logger import get_logger

logger = get_logger(__name__)


class AuthClient(BaseClient):
    """Client for authentication endpoints."""

    ENDPOINT = "/auth"

    @allure.step("Create authentication token")
    def create_token(self, username: str, password: str) -> str:
        """Authenticate and return a token string.

        Args:
            username: Auth username.
            password: Auth password.

        Returns:
            Token string for authorized requests.

        Raises:
            ValueError: If authentication fails or token is missing.
        """
        payload = {"username": username, "password": password}
        response = self.post(self.ENDPOINT, json_data=payload)

        if response.status_code != 200:
            logger.error(f"Authentication failed with status {response.status_code}")
            raise ValueError(f"Authentication failed: {response.status_code}")

        data = response.json()
        token = data.get("token")

        if not token:
            reason = data.get("reason", "Unknown error")
            logger.error(f"No token in response: {reason}")
            raise ValueError(f"Authentication failed: {reason}")

        # Validate response structure via Pydantic
        AuthResponse(**data)

        logger.info("Authentication successful, token obtained")
        return token

    @allure.step("Create authentication token (raw response)")
    def create_token_raw(self, username: str, password: str):
        """Return the raw response for authentication (useful for negative tests)."""
        payload = {"username": username, "password": password}
        return self.post(self.ENDPOINT, json_data=payload)
