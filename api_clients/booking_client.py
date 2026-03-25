from typing import Any, Dict, List, Optional

import allure
import requests

from api_clients.base_client import BaseClient
from utils.logger import get_logger

logger = get_logger(__name__)


class BookingClient(BaseClient):
    """Client for booking CRUD endpoints."""

    ENDPOINT = "/booking"

    def _auth_headers(self, token: str) -> dict:
        """Build headers with cookie-based auth token."""
        return {"Cookie": f"token={token}"}

    @allure.step("Get all booking IDs")
    def get_booking_ids(
        self, params: Optional[Dict[str, Any]] = None
    ) -> List[dict]:
        """Get list of booking IDs, optionally filtered."""
        response = self.get(self.ENDPOINT, params=params)
        response.raise_for_status()
        return response.json()

    @allure.step("Get booking by ID: {booking_id}")
    def get_booking(self, booking_id: int) -> requests.Response:
        """Get a single booking by ID."""
        return self.get(f"{self.ENDPOINT}/{booking_id}")

    @allure.step("Create a new booking")
    def create_booking(self, booking_data: dict) -> requests.Response:
        """Create a new booking."""
        return self.post(self.ENDPOINT, json_data=booking_data)

    @allure.step("Update booking ID: {booking_id}")
    def update_booking(
        self, booking_id: int, booking_data: dict, token: str
    ) -> requests.Response:
        """Full update of a booking (PUT)."""
        return self.put(
            f"{self.ENDPOINT}/{booking_id}",
            json_data=booking_data,
            headers=self._auth_headers(token),
        )

    @allure.step("Partial update booking ID: {booking_id}")
    def partial_update_booking(
        self, booking_id: int, booking_data: dict, token: str
    ) -> requests.Response:
        """Partial update of a booking (PATCH)."""
        return self.patch(
            f"{self.ENDPOINT}/{booking_id}",
            json_data=booking_data,
            headers=self._auth_headers(token),
        )

    @allure.step("Delete booking ID: {booking_id}")
    def delete_booking(self, booking_id: int, token: str) -> requests.Response:
        """Delete a booking."""
        return self.delete(
            f"{self.ENDPOINT}/{booking_id}",
            headers=self._auth_headers(token),
        )
