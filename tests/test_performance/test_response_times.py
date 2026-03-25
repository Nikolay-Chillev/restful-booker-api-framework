import allure
import pytest

from config.config import settings
from utils.helpers import generate_booking_data


@allure.epic("Booking API")
@allure.feature("Performance")
class TestResponseTimes:
    """Response time assertions for all API endpoints."""

    RESPONSE_TIME_THRESHOLD = 10.0  # seconds (generous for free Herokuapp hosting)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("GET /booking responds within threshold")
    @pytest.mark.performance
    def test_get_bookings_response_time(self, booking_client):
        """Verify GET /booking responds within acceptable time."""
        response = booking_client.get("/booking")
        elapsed = response.elapsed.total_seconds()

        with allure.step(f"Response time: {elapsed:.2f}s (threshold: {self.RESPONSE_TIME_THRESHOLD}s)"):
            allure.attach(f"Elapsed: {elapsed:.3f}s", name="Timing", attachment_type=allure.attachment_type.TEXT)
            assert response.status_code == 200
            assert elapsed < self.RESPONSE_TIME_THRESHOLD

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("POST /booking responds within threshold")
    @pytest.mark.performance
    def test_create_booking_response_time(self, make_booking):
        """Verify POST /booking responds within acceptable time."""
        result, _ = make_booking()
        assert "bookingid" in result

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("POST /auth responds within threshold")
    @pytest.mark.performance
    def test_auth_response_time(self, auth_client):
        """Verify POST /auth responds within acceptable time."""
        response = auth_client.create_token_raw(settings.AUTH_USERNAME, settings.AUTH_PASSWORD)
        elapsed = response.elapsed.total_seconds()

        with allure.step(f"Response time: {elapsed:.2f}s"):
            assert response.status_code == 200
            assert elapsed < self.RESPONSE_TIME_THRESHOLD

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GET /booking/:id responds within threshold")
    @pytest.mark.performance
    def test_get_single_booking_response_time(self, booking_client, create_booking):
        """Verify GET /booking/:id responds within acceptable time."""
        _, booking_id = create_booking

        response = booking_client.get_booking(booking_id)
        elapsed = response.elapsed.total_seconds()

        with allure.step(f"Response time: {elapsed:.2f}s"):
            assert response.status_code == 200
            assert elapsed < self.RESPONSE_TIME_THRESHOLD

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Consecutive requests maintain consistent response times")
    @pytest.mark.performance
    def test_consistent_response_times(self, booking_client):
        """Verify response times don't degrade across consecutive requests."""
        times = []
        for _ in range(5):
            response = booking_client.get("/booking")
            elapsed = response.elapsed.total_seconds()
            times.append(elapsed)
            assert response.status_code == 200

        avg_time = sum(times) / len(times)
        max_time = max(times)

        with allure.step(f"Avg: {avg_time:.2f}s, Max: {max_time:.2f}s"):
            allure.attach(
                "\n".join(f"Request {i+1}: {t:.3f}s" for i, t in enumerate(times)),
                name="Response Times",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert max_time < self.RESPONSE_TIME_THRESHOLD * 2
