import allure
import pytest

from utils.helpers import generate_booking_data


@allure.epic("Booking API")
@allure.feature("Idempotency")
class TestIdempotency:
    """Tests verifying idempotent behavior of API operations."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("PUT /booking/:id is idempotent")
    @pytest.mark.idempotency
    def test_put_is_idempotent(self, booking_client, create_booking, auth_token):
        """Verify sending the same PUT request twice produces identical results."""
        _, booking_id = create_booking
        update_data = generate_booking_data()

        with allure.step("First PUT request"):
            response1 = booking_client.update_booking(booking_id, update_data, auth_token)
            assert response1.status_code == 200
            data1 = response1.json()

        with allure.step("Second PUT request (identical)"):
            response2 = booking_client.update_booking(booking_id, update_data, auth_token)
            assert response2.status_code == 200
            data2 = response2.json()

        with allure.step("Verify both responses are identical"):
            assert data1["firstname"] == data2["firstname"]
            assert data1["lastname"] == data2["lastname"]
            assert data1["totalprice"] == data2["totalprice"]
            assert data1["depositpaid"] == data2["depositpaid"]

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("GET /booking/:id is idempotent")
    @pytest.mark.idempotency
    def test_get_is_idempotent(self, booking_client, create_booking):
        """Verify multiple GET requests return identical data."""
        _, booking_id = create_booking

        with allure.step("Send 3 consecutive GET requests"):
            responses = [
                booking_client.get_booking(booking_id).json()
                for _ in range(3)
            ]

        with allure.step("Verify all responses are identical"):
            for i in range(1, len(responses)):
                assert responses[0] == responses[i], (
                    f"Response {i+1} differs from response 1"
                )

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("DELETE /booking/:id returns error on second call")
    @pytest.mark.idempotency
    def test_delete_not_idempotent(self, booking_client, auth_token):
        """Verify DELETE returns error when called twice on same resource."""
        data = generate_booking_data()
        create_response = booking_client.create_booking(data)
        booking_id = create_response.json()["bookingid"]

        with allure.step("First DELETE"):
            response1 = booking_client.delete_booking(booking_id, auth_token)
            assert response1.status_code == 201

        with allure.step("Second DELETE (resource already gone)"):
            response2 = booking_client.delete_booking(booking_id, auth_token)
            assert response2.status_code == 405, (
                "Second DELETE should fail since resource is gone"
            )
