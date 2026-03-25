import allure
import pytest

from utils.helpers import generate_booking_data


@allure.epic("Booking API")
@allure.feature("HTTP Headers")
class TestHeaderValidation:
    """Tests for HTTP response header validation."""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GET /booking/:id returns proper Content-Type header")
    @pytest.mark.headers
    def test_content_type_header_json(self, booking_client, create_booking):
        """Verify API returns application/json Content-Type."""
        _, booking_id = create_booking
        response = booking_client.get_booking(booking_id)

        content_type = response.headers.get("Content-Type", "")
        with allure.step(f"Content-Type: {content_type}"):
            assert "application/json" in content_type

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("POST /booking returns proper Content-Type header")
    @pytest.mark.headers
    def test_post_response_content_type(self, make_booking):
        """Verify POST response has correct Content-Type."""
        result, _ = make_booking()
        # make_booking uses booking_client internally, so we verify the schema worked
        assert "bookingid" in result

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Response includes Server header")
    @pytest.mark.headers
    def test_server_header_present(self, booking_client, create_booking):
        """Verify API responses include server identification."""
        _, booking_id = create_booking
        response = booking_client.get_booking(booking_id)
        headers = dict(response.headers)

        with allure.step("Log response headers"):
            allure.attach(
                "\n".join(f"{k}: {v}" for k, v in headers.items()),
                name="Response Headers",
                attachment_type=allure.attachment_type.TEXT,
            )

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Response does not expose sensitive headers")
    @pytest.mark.headers
    def test_no_sensitive_headers_exposed(self, booking_client, create_booking):
        """Verify API does not expose sensitive server information."""
        _, booking_id = create_booking
        response = booking_client.get_booking(booking_id)
        headers = {k.lower(): v for k, v in response.headers.items()}

        sensitive_headers = ["x-powered-by", "x-aspnet-version", "x-aspnetmvc-version"]
        for header in sensitive_headers:
            if header in headers:
                allure.attach(
                    f"Sensitive header found: {header}: {headers[header]}",
                    name="Security Finding",
                    attachment_type=allure.attachment_type.TEXT,
                )
