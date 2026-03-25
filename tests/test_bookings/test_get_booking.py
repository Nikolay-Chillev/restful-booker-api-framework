import allure
import pytest


@allure.epic("Booking API")
@allure.feature("Get Booking")
class TestGetBooking:
    """Tests for GET /booking and GET /booking/:id endpoints."""

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Get all booking IDs returns a list")
    @pytest.mark.smoke
    def test_get_all_booking_ids(self, booking_client):
        """Verify GET /booking returns a list of booking IDs."""
        with allure.step("Send GET /booking request"):
            ids = booking_client.get_booking_ids()

        with allure.step("Verify response is a non-empty list"):
            assert isinstance(ids, list)
            assert len(ids) > 0

        with allure.step("Verify each item has bookingid"):
            for item in ids[:5]:
                assert "bookingid" in item

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Get specific booking by ID")
    @pytest.mark.smoke
    def test_get_booking_by_id(self, booking_client, create_booking):
        """Verify GET /booking/:id returns correct booking data."""
        booking_data, booking_id = create_booking

        with allure.step(f"Send GET /booking/{booking_id}"):
            response = booking_client.get_booking(booking_id)

        with allure.step("Verify response status and data"):
            assert response.status_code == 200
            data = response.json()
            assert data["firstname"] == booking_data["booking"]["firstname"]
            assert data["lastname"] == booking_data["booking"]["lastname"]

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Get non-existent booking returns 404")
    @pytest.mark.regression
    def test_get_nonexistent_booking(self, booking_client):
        """Verify GET /booking/:id with invalid ID returns 404."""
        response = booking_client.get_booking(999999999)
        assert response.status_code == 404

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Filter bookings by firstname")
    @pytest.mark.regression
    def test_filter_bookings_by_firstname(self, booking_client, create_booking):
        """Verify GET /booking?firstname=X returns filtered results."""
        booking_data, booking_id = create_booking
        firstname = booking_data["booking"]["firstname"]

        with allure.step(f"Filter bookings by firstname={firstname}"):
            ids = booking_client.get_booking_ids(params={"firstname": firstname})

        with allure.step("Verify created booking is in filtered results"):
            booking_ids = [item["bookingid"] for item in ids]
            assert booking_id in booking_ids

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Filter bookings by checkin and checkout dates")
    @pytest.mark.regression
    def test_filter_bookings_by_dates(self, booking_client, create_booking):
        """Verify GET /booking with date filters returns results."""
        booking_data, booking_id = create_booking
        dates = booking_data["booking"]["bookingdates"]

        with allure.step("Filter bookings by checkin/checkout"):
            ids = booking_client.get_booking_ids(
                params={"checkin": dates["checkin"], "checkout": dates["checkout"]}
            )

        with allure.step("Verify response is a list"):
            assert isinstance(ids, list)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Get booking response contains all expected fields")
    @pytest.mark.regression
    def test_get_booking_response_structure(self, booking_client, create_booking):
        """Verify response contains all expected fields with correct types."""
        _, booking_id = create_booking

        response = booking_client.get_booking(booking_id)
        data = response.json()

        with allure.step("Verify all required fields are present"):
            assert "firstname" in data
            assert "lastname" in data
            assert "totalprice" in data
            assert "depositpaid" in data
            assert "bookingdates" in data
            assert "checkin" in data["bookingdates"]
            assert "checkout" in data["bookingdates"]

        with allure.step("Verify field types"):
            assert isinstance(data["firstname"], str)
            assert isinstance(data["lastname"], str)
            assert isinstance(data["totalprice"], int)
            assert isinstance(data["depositpaid"], bool)
