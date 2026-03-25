import allure
import pytest

from config.config import settings
from utils.helpers import generate_booking_data
from utils.schema_validator import validate_schema


@allure.epic("Booking API")
@allure.feature("Contract Testing")
class TestSchemaValidation:
    """Contract tests validating API responses against JSON Schemas."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("GET /booking/:id matches booking schema")
    @pytest.mark.contract
    def test_get_booking_schema(self, booking_client, create_booking):
        """Verify GET /booking/:id response matches the booking JSON schema."""
        _, booking_id = create_booking

        with allure.step(f"GET /booking/{booking_id}"):
            response = booking_client.get_booking(booking_id)
            assert response.status_code == 200

        with allure.step("Validate response against booking schema"):
            validate_schema(response.json(), "booking_schema.json")

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("POST /booking response matches create booking schema")
    @pytest.mark.contract
    def test_create_booking_schema(self, booking_client, auth_token):
        """Verify POST /booking response matches the create booking JSON schema."""
        data = generate_booking_data()

        with allure.step("Create a booking"):
            response = booking_client.create_booking(data)
            assert response.status_code == 200

        with allure.step("Validate response against create booking schema"):
            validate_schema(response.json(), "create_booking_schema.json")

        booking_client.delete_booking(response.json()["bookingid"], auth_token)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("POST /auth response matches auth schema")
    @pytest.mark.contract
    def test_auth_response_schema(self, auth_client):
        """Verify POST /auth response matches the auth JSON schema."""
        with allure.step("Authenticate"):
            response = auth_client.create_token_raw(
                settings.AUTH_USERNAME, settings.AUTH_PASSWORD
            )
            assert response.status_code == 200

        with allure.step("Validate response against auth schema"):
            validate_schema(response.json(), "auth_schema.json")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GET /booking (list) returns array of booking IDs")
    @pytest.mark.contract
    def test_booking_ids_list_schema(self, booking_client):
        """Verify GET /booking returns an array of objects with bookingid."""
        ids = booking_client.get_booking_ids()

        with allure.step("Validate list structure"):
            assert isinstance(ids, list)
            if len(ids) > 0:
                assert "bookingid" in ids[0]
                assert isinstance(ids[0]["bookingid"], int)
