import allure
import pytest

from utils.helpers import generate_booking_data


@allure.epic("Booking API")
@allure.feature("Partial Update Booking")
class TestPartialUpdateBooking:
    """Tests for PATCH /booking/:id endpoint."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Partial update single field (firstname)")
    @pytest.mark.smoke
    def test_partial_update_single_field(self, booking_client, create_booking, auth_token):
        """Verify PATCH can update a single field."""
        booking_data, booking_id = create_booking

        with allure.step("Send PATCH with only firstname"):
            response = booking_client.partial_update_booking(
                booking_id, {"firstname": "UpdatedName"}, auth_token
            )

        with allure.step("Verify firstname is updated"):
            assert response.status_code == 200
            data = response.json()
            assert data["firstname"] == "UpdatedName"

        with allure.step("Verify other fields remain unchanged"):
            assert data["lastname"] == booking_data["booking"]["lastname"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Partial update multiple fields")
    @pytest.mark.regression
    def test_partial_update_multiple_fields(self, booking_client, create_booking, auth_token):
        """Verify PATCH can update multiple fields simultaneously."""
        _, booking_id = create_booking

        with allure.step("Send PATCH with firstname and totalprice"):
            response = booking_client.partial_update_booking(
                booking_id,
                {"firstname": "MultiUpdate", "totalprice": 999},
                auth_token,
            )

        with allure.step("Verify both fields are updated"):
            assert response.status_code == 200
            data = response.json()
            assert data["firstname"] == "MultiUpdate"
            assert data["totalprice"] == 999

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Partial update without auth returns 403")
    @pytest.mark.negative
    def test_partial_update_no_auth(self, booking_client, create_booking):
        """Verify PATCH without valid token returns 403."""
        _, booking_id = create_booking

        response = booking_client.partial_update_booking(
            booking_id, {"firstname": "Unauthorized"}, token="invalid"
        )
        assert response.status_code == 403

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Partial update preserves unchanged fields")
    @pytest.mark.regression
    def test_partial_update_preserves_fields(self, booking_client, create_booking, auth_token):
        """Verify unchanged fields remain intact after PATCH."""
        booking_data, booking_id = create_booking
        original = booking_data["booking"]

        booking_client.partial_update_booking(
            booking_id, {"firstname": "OnlyThisChanged"}, auth_token
        )

        with allure.step("GET the updated booking"):
            response = booking_client.get_booking(booking_id)
            data = response.json()

        with allure.step("Verify unchanged fields are preserved"):
            assert data["lastname"] == original["lastname"]
            assert data["totalprice"] == original["totalprice"]
            assert data["depositpaid"] == original["depositpaid"]
