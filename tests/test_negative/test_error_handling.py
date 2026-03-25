import allure
import pytest

from utils.helpers import generate_booking_data, load_test_data

# Expected behavior vs actual behavior tracking.
# Restful Booker lacks input validation — these tests document known issues
# so that if the API is fixed in the future, the tests will catch the change.
BUG_API_ACCEPTS_INVALID_DATES = "KNOWN-BUG-001: API accepts invalid date formats without validation"
BUG_API_ACCEPTS_STRING_PRICE = "KNOWN-BUG-002: API accepts string value for totalprice (type coercion)"
BUG_API_ACCEPTS_LONG_NAMES = "KNOWN-BUG-003: API accepts extremely long strings without length validation"
BUG_API_STORES_XSS_PAYLOAD = "KNOWN-BUG-004: API stores XSS/injection payloads without sanitization"


def _report_known_bug(bug_id: str, expected: str, actual: str) -> None:
    """Attach a known bug report to the Allure report."""
    allure.attach(
        f"Bug: {bug_id}\nExpected: {expected}\nActual: {actual}",
        name=f"Known Bug: {bug_id.split(':')[0]}",
        attachment_type=allure.attachment_type.TEXT,
    )


@allure.epic("Booking API")
@allure.feature("Error Handling")
class TestErrorHandling:
    """Negative tests for invalid inputs and error scenarios.

    Several tests document known API bugs where invalid input is accepted
    instead of being rejected. These are tracked as known issues.
    """

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with missing required fields")
    @pytest.mark.negative
    def test_create_booking_missing_fields(self, booking_client):
        """Verify API rejects booking with missing required fields."""
        response = booking_client.create_booking({"firstname": "OnlyFirst"})

        with allure.step("Verify response indicates error"):
            assert response.status_code in [400, 500], (
                f"Expected 400/500, got {response.status_code}"
            )

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with empty body")
    @pytest.mark.negative
    def test_create_booking_empty_body(self, booking_client):
        """Verify API rejects empty request body."""
        response = booking_client.create_booking({})
        assert response.status_code in [400, 500], (
            f"Expected 400/500, got {response.status_code}"
        )

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with invalid date format")
    @allure.issue(BUG_API_ACCEPTS_INVALID_DATES)
    @pytest.mark.negative
    def test_create_booking_invalid_dates(self, booking_client, auth_token):
        """Verify API handles invalid date formats.

        Known bug: API accepts 'not-a-date' without validation.
        Expected: 400 Bad Request.
        """
        data = generate_booking_data()
        data["bookingdates"] = {"checkin": "not-a-date", "checkout": "also-not"}

        response = booking_client.create_booking(data)

        if response.status_code == 200:
            _report_known_bug(
                BUG_API_ACCEPTS_INVALID_DATES,
                expected="400 Bad Request — dates should be validated",
                actual=f"200 OK — booking created with invalid dates",
            )
            booking_client.delete_booking(response.json()["bookingid"], auth_token)
        else:
            with allure.step("API correctly rejected invalid dates"):
                assert response.status_code in [400, 422]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with string instead of number for price")
    @allure.issue(BUG_API_ACCEPTS_STRING_PRICE)
    @pytest.mark.negative
    def test_create_booking_string_price(self, booking_client, auth_token):
        """Verify API rejects wrong data type for totalprice.

        Known bug: API accepts string value and coerces to 0.
        Expected: 400 Bad Request.
        """
        data = generate_booking_data()
        data["totalprice"] = "not_a_number"

        response = booking_client.create_booking(data)

        if response.status_code == 200:
            _report_known_bug(
                BUG_API_ACCEPTS_STRING_PRICE,
                expected="400 Bad Request — totalprice should be integer",
                actual=f"200 OK — booking created with string price",
            )
            booking_client.delete_booking(response.json()["bookingid"], auth_token)
        else:
            with allure.step("API correctly rejected string price"):
                assert response.status_code in [400, 422]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with extremely long name")
    @allure.issue(BUG_API_ACCEPTS_LONG_NAMES)
    @pytest.mark.negative
    def test_create_booking_long_name(self, booking_client, auth_token):
        """Verify API rejects extremely long string values.

        Known bug: API accepts 5000-character firstname without validation.
        Expected: 400 Bad Request with field length error.
        """
        data = generate_booking_data()
        data["firstname"] = "A" * 5000

        response = booking_client.create_booking(data)

        if response.status_code == 200:
            _report_known_bug(
                BUG_API_ACCEPTS_LONG_NAMES,
                expected="400 Bad Request — firstname too long",
                actual=f"200 OK — booking created with 5000-char name",
            )
            booking_client.delete_booking(response.json()["bookingid"], auth_token)
        else:
            with allure.step("API correctly rejected long name"):
                assert response.status_code in [400, 413, 422]

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Security: {payload_name} in firstname field")
    @allure.issue(BUG_API_STORES_XSS_PAYLOAD)
    @pytest.mark.parametrize(
        "payload_name,payload",
        [
            pytest.param("SQL injection", "'; DROP TABLE bookings; --", id="sql-injection"),
            pytest.param("XSS", "<script>alert('xss')</script>", id="xss-script-tag"),
            pytest.param("Path traversal", "../../etc/passwd", id="path-traversal"),
            pytest.param("Command injection", "; rm -rf /", id="command-injection"),
        ],
    )
    @pytest.mark.negative
    def test_security_payloads(self, booking_client, auth_token, payload_name, payload):
        """Verify API sanitizes or rejects dangerous payloads.

        Known bug: API stores payloads as-is without sanitization.
        Expected: 400 Bad Request or sanitized storage.
        """
        data = generate_booking_data()
        data["firstname"] = payload

        response = booking_client.create_booking(data)

        with allure.step(f"Check API response for {payload_name}"):
            assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            booking_id = response.json()["bookingid"]
            get_response = booking_client.get_booking(booking_id)

            if get_response.status_code == 200:
                stored_value = get_response.json()["firstname"]
                if stored_value == payload:
                    _report_known_bug(
                        BUG_API_STORES_XSS_PAYLOAD,
                        expected=f"Sanitized or rejected {payload_name} payload",
                        actual=f"Stored raw payload: {payload[:50]}",
                    )
                else:
                    with allure.step("API sanitized the payload"):
                        allure.attach(
                            f"Input: {payload}\nStored: {stored_value}",
                            name="Sanitization Result",
                            attachment_type=allure.attachment_type.TEXT,
                        )

            booking_client.delete_booking(booking_id, auth_token)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Data-driven negative test: invalid payload")
    @pytest.mark.parametrize(
        "test_case",
        load_test_data(
            "invalid_booking_data.json",
            id_func=lambda item: item["description"].lower().replace(" ", "-"),
        ),
    )
    @pytest.mark.negative
    def test_invalid_payloads_from_file(self, booking_client, auth_token, test_case):
        """Verify API behavior with various invalid payloads from JSON file."""
        payload = test_case["data"]
        description = test_case["description"]

        response = booking_client.create_booking(payload)

        if response.status_code == 200:
            _report_known_bug(
                f"KNOWN-BUG: API accepts {description}",
                expected="400/422 — invalid payload should be rejected",
                actual=f"200 OK — booking created despite: {description}",
            )
            try:
                booking_client.delete_booking(response.json()["bookingid"], auth_token)
            except Exception:
                pass
        else:
            with allure.step(f"API correctly rejected: {description}"):
                allure.attach(
                    f"Status: {response.status_code}",
                    name="Rejection Response",
                    attachment_type=allure.attachment_type.TEXT,
                )
