import allure
import pytest

from utils.helpers import generate_booking_data


@allure.epic("Booking API")
@allure.feature("Delete Booking")
class TestDeleteBooking:
    """Tests for DELETE /booking/:id endpoint."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Delete existing booking successfully")
    @pytest.mark.smoke
    def test_delete_booking_success(self, booking_client, auth_token):
        """Verify that a booking can be deleted with valid token."""
        # Create a booking to delete (don't use create_booking fixture — it auto-cleans)
        data = generate_booking_data()
        create_response = booking_client.create_booking(data)
        booking_id = create_response.json()["bookingid"]

        with allure.step(f"Delete booking {booking_id}"):
            response = booking_client.delete_booking(booking_id, auth_token)

        with allure.step("Verify deletion response"):
            assert response.status_code == 201

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Deleted booking returns 404 on GET")
    @pytest.mark.regression
    def test_deleted_booking_not_found(self, booking_client, auth_token):
        """Verify that a deleted booking returns 404 on subsequent GET."""
        data = generate_booking_data()
        create_response = booking_client.create_booking(data)
        booking_id = create_response.json()["bookingid"]

        booking_client.delete_booking(booking_id, auth_token)

        with allure.step(f"GET deleted booking {booking_id}"):
            response = booking_client.get_booking(booking_id)

        with allure.step("Verify 404 response"):
            assert response.status_code == 404

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Delete booking without auth returns 403")
    @pytest.mark.negative
    def test_delete_booking_no_auth(self, booking_client, auth_token):
        """Verify that deleting without auth returns 403."""
        data = generate_booking_data()
        create_response = booking_client.create_booking(data)
        booking_id = create_response.json()["bookingid"]

        with allure.step("Delete without valid token"):
            response = booking_client.delete_booking(booking_id, token="invalid")

        with allure.step("Verify 403 response"):
            assert response.status_code == 403

        # Cleanup
        booking_client.delete_booking(booking_id, auth_token)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Delete non-existent booking returns error")
    @pytest.mark.negative
    def test_delete_nonexistent_booking(self, booking_client, auth_token):
        """Verify that deleting a non-existent booking returns an error."""
        response = booking_client.delete_booking(999999999, auth_token)
        assert response.status_code == 405
