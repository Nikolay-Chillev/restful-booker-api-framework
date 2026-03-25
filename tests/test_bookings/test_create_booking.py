import allure
import pytest

from utils.helpers import generate_booking_data, load_test_data


@allure.epic("Booking API")
@allure.feature("Create Booking")
class TestCreateBooking:
    """Tests for POST /booking endpoint."""

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Create booking with valid data")
    @pytest.mark.smoke
    def test_create_booking_success(self, make_booking):
        """Verify that a booking can be created with valid data."""
        result, booking_id = make_booking()

        with allure.step("Verify response contains bookingid"):
            assert "bookingid" in result
            assert isinstance(result["bookingid"], int)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Created booking fields match request data")
    @pytest.mark.regression
    def test_create_booking_fields_match(self, make_booking, booking_data):
        """Verify that all fields in the response match the request."""
        result, _ = make_booking(**booking_data)
        booking = result["booking"]

        with allure.step("Verify all fields match"):
            assert booking["firstname"] == booking_data["firstname"]
            assert booking["lastname"] == booking_data["lastname"]
            assert booking["totalprice"] == booking_data["totalprice"]
            assert booking["depositpaid"] == booking_data["depositpaid"]
            assert booking["bookingdates"]["checkin"] == booking_data["bookingdates"]["checkin"]
            assert booking["bookingdates"]["checkout"] == booking_data["bookingdates"]["checkout"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking without additionalneeds")
    @pytest.mark.regression
    def test_create_booking_without_additional_needs(self, make_booking):
        """Verify booking can be created without optional additionalneeds field."""
        data = generate_booking_data()
        data.pop("additionalneeds", None)
        result, _ = make_booking(**data)
        assert "bookingid" in result

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Create booking returns unique booking ID")
    @pytest.mark.regression
    def test_create_booking_unique_id(self, make_booking):
        """Verify that each created booking gets a unique ID."""
        ids = [make_booking()[1] for _ in range(3)]

        with allure.step("Verify all IDs are unique"):
            assert len(ids) == len(set(ids)), "Booking IDs should be unique"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Data-driven: Create booking with parametrized test data")
    @pytest.mark.parametrize(
        "test_data",
        load_test_data(
            "booking_data.json",
            id_func=lambda item: f"{item['firstname']}-{item['lastname']}",
        ),
    )
    @pytest.mark.regression
    def test_create_booking_data_driven(self, make_booking, test_data):
        """Verify booking creation with multiple data sets from JSON file."""
        with allure.step(f"Create booking for {test_data['firstname']} {test_data['lastname']}"):
            result, _ = make_booking(**test_data)
            assert "bookingid" in result

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with depositpaid={deposit_paid}")
    @pytest.mark.parametrize(
        "deposit_paid",
        [
            pytest.param(True, id="deposit-paid"),
            pytest.param(False, id="deposit-not-paid"),
        ],
    )
    @pytest.mark.regression
    def test_create_booking_deposit_variations(self, make_booking, deposit_paid):
        """Verify booking creation with both depositpaid values."""
        result, _ = make_booking(depositpaid=deposit_paid)
        assert result["booking"]["depositpaid"] == deposit_paid
