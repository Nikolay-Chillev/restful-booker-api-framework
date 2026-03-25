import allure
import pytest

from utils.helpers import generate_booking_data


@allure.epic("Booking API")
@allure.feature("Update Booking")
class TestUpdateBooking:
    """Tests for PUT /booking/:id endpoint."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Full update booking with valid token")
    @pytest.mark.smoke
    def test_update_booking_success(self, booking_client, create_booking, auth_token):
        """Verify that a booking can be fully updated with PUT."""
        _, booking_id = create_booking
        new_data = generate_booking_data()

        with allure.step("Send PUT request with new data"):
            response = booking_client.update_booking(booking_id, new_data, auth_token)

        with allure.step("Verify response status is 200"):
            assert response.status_code == 200

        with allure.step("Verify updated fields match"):
            data = response.json()
            assert data["firstname"] == new_data["firstname"]
            assert data["lastname"] == new_data["lastname"]
            assert data["totalprice"] == new_data["totalprice"]

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify updated booking persists on GET")
    @pytest.mark.regression
    def test_update_booking_persists(self, booking_client, create_booking, auth_token):
        """Verify that changes from PUT are visible on subsequent GET."""
        _, booking_id = create_booking
        new_data = generate_booking_data()

        booking_client.update_booking(booking_id, new_data, auth_token)

        with allure.step("GET the updated booking"):
            response = booking_client.get_booking(booking_id)
            data = response.json()

        with allure.step("Verify persisted data matches update"):
            assert data["firstname"] == new_data["firstname"]
            assert data["lastname"] == new_data["lastname"]

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Update booking without token returns 403")
    @pytest.mark.negative
    def test_update_booking_no_auth(self, booking_client, create_booking):
        """Verify that updating without auth returns 403."""
        _, booking_id = create_booking
        new_data = generate_booking_data()

        with allure.step("Send PUT without auth token"):
            response = booking_client.update_booking(booking_id, new_data, token="invalid_token")

        with allure.step("Verify 403 response"):
            assert response.status_code == 403

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Update non-existent booking returns error")
    @pytest.mark.negative
    def test_update_nonexistent_booking(self, booking_client, auth_token):
        """Verify that updating a non-existent booking returns an error."""
        new_data = generate_booking_data()
        response = booking_client.update_booking(999999999, new_data, auth_token)
        assert response.status_code == 405
