import allure
import pytest

from utils.helpers import generate_booking_data


@allure.epic("Booking API")
@allure.feature("Boundary Testing")
class TestBoundaryValues:
    """Boundary value and edge case tests for booking fields."""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with totalprice={price}")
    @pytest.mark.parametrize(
        "price",
        [
            pytest.param(0, id="zero-price"),
            pytest.param(1, id="min-price"),
            pytest.param(999999, id="very-large-price"),
        ],
    )
    @pytest.mark.boundary
    def test_totalprice_boundary_values(self, make_booking, price):
        """Verify booking creation with boundary totalprice values."""
        result, _ = make_booking(totalprice=price)
        assert result["booking"]["totalprice"] == price

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with name length={length}")
    @pytest.mark.parametrize(
        "length",
        [
            pytest.param(1, id="single-char-name"),
            pytest.param(50, id="medium-name"),
            pytest.param(255, id="max-typical-name"),
        ],
    )
    @pytest.mark.boundary
    def test_name_length_boundary(self, make_booking, length):
        """Verify booking creation with various name lengths."""
        name = "A" * length
        result, _ = make_booking(firstname=name)
        assert result["booking"]["firstname"] == name

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with special characters in name")
    @pytest.mark.parametrize(
        "name,desc",
        [
            pytest.param("O'Brien", "apostrophe", id="apostrophe"),
            pytest.param("Mary-Jane", "hyphen", id="hyphen"),
            pytest.param("Jose Luis", "space", id="space"),
            pytest.param("Muller", "umlaut-ascii", id="ascii-name"),
            pytest.param("Jean-Pierre", "double-hyphen", id="double-part-name"),
        ],
    )
    @pytest.mark.boundary
    def test_special_characters_in_name(self, make_booking, name, desc):
        """Verify booking creation with special characters in firstname."""
        result, booking_id = make_booking(firstname=name)
        assert result["booking"]["firstname"] == name

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with same checkin and checkout date")
    @pytest.mark.boundary
    def test_same_checkin_checkout_date(self, make_booking):
        """Verify booking with same-day checkin and checkout."""
        data = generate_booking_data()
        data["bookingdates"]["checkout"] = data["bookingdates"]["checkin"]
        result, _ = make_booking(**data)
        dates = result["booking"]["bookingdates"]
        assert dates["checkin"] == dates["checkout"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with far-future dates")
    @pytest.mark.boundary
    def test_far_future_dates(self, make_booking):
        """Verify booking creation with dates far in the future."""
        result, _ = make_booking(
            bookingdates={"checkin": "2030-01-01", "checkout": "2030-12-31"}
        )
        dates = result["booking"]["bookingdates"]
        assert "2030" in dates["checkin"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with past dates")
    @pytest.mark.boundary
    def test_past_dates(self, make_booking):
        """Verify booking creation with historical dates."""
        result, _ = make_booking(
            bookingdates={"checkin": "2020-01-01", "checkout": "2020-01-05"}
        )
        assert result["booking"]["bookingdates"]["checkin"] == "2020-01-01"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GET /booking with invalid ID type: {booking_id}")
    @pytest.mark.parametrize(
        "booking_id",
        [
            pytest.param(0, id="zero-id"),
            pytest.param(-1, id="negative-id"),
            pytest.param("abc", id="string-id"),
        ],
    )
    @pytest.mark.boundary
    def test_get_booking_invalid_id_types(self, booking_client, booking_id):
        """Verify API handles invalid booking ID types."""
        response = booking_client.get(f"/booking/{booking_id}")
        assert response.status_code in [400, 404]
