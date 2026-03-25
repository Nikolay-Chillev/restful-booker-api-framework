import pytest
import requests

from api_clients.auth_client import AuthClient
from api_clients.booking_client import BookingClient
from config.config import settings
from models.booking_model import BookingResponse, Booking
from utils.helpers import generate_booking_data
from utils.logger import get_logger
from utils.retry import retry

logger = get_logger(__name__)


def _validate_booking_response(data: dict) -> BookingResponse:
    """Validate API response against Pydantic BookingResponse model.

    Raises ValidationError if the response structure doesn't match the model.
    """
    return BookingResponse(**data)


def _validate_booking(data: dict) -> Booking:
    """Validate a single booking against Pydantic Booking model."""
    return Booking(**data)


@retry(
    max_attempts=settings.RETRY_ATTEMPTS,
    delay=settings.RETRY_DELAY,
    exceptions=(requests.RequestException, ValueError),
)
def _create_auth_token(auth_client: AuthClient) -> str:
    """Create auth token with retry on network failures."""
    return auth_client.create_token(settings.AUTH_USERNAME, settings.AUTH_PASSWORD)


@retry(
    max_attempts=settings.RETRY_ATTEMPTS,
    delay=settings.RETRY_DELAY,
    exceptions=(requests.RequestException, AssertionError),
)
def _create_booking_with_retry(booking_client: BookingClient, data: dict) -> dict:
    """Create a booking with retry on transient failures."""
    response = booking_client.create_booking(data)
    assert response.status_code == 200, f"Failed to create booking: {response.text}"
    return response.json()


def _cleanup_booking(booking_client: BookingClient, booking_id: int, token: str) -> None:
    """Delete a booking, logging but not raising on failure."""
    try:
        booking_client.delete_booking(booking_id, token)
        logger.info(f"Cleaned up booking ID: {booking_id}")
    except Exception as e:
        logger.warning(f"Cleanup failed for booking {booking_id}: {e}")


@pytest.fixture(scope="session")
def auth_client():
    """Session-scoped auth client instance."""
    client = AuthClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def booking_client():
    """Session-scoped booking client instance."""
    client = BookingClient()
    yield client
    client.close()


@pytest.fixture(scope="module")
def auth_token(auth_client):
    """Module-scoped auth token with retry — refreshes per test module."""
    logger.info("Obtaining auth token for test module")
    return _create_auth_token(auth_client)


@pytest.fixture
def booking_data():
    """Generate random valid booking data for a single test."""
    return generate_booking_data()


@pytest.fixture
def make_booking(booking_client, auth_token):
    """Factory fixture that creates bookings with retry and automatic cleanup.

    Validates the response against the Pydantic BookingResponse model.

    Usage:
        def test_example(make_booking):
            data, booking_id = make_booking()
            data, booking_id = make_booking(firstname="Custom")
    """
    created_ids = []

    def _make_booking(**overrides):
        data = generate_booking_data()
        data.update(overrides)

        result = _create_booking_with_retry(booking_client, data)

        # Pydantic validation
        validated = _validate_booking_response(result)
        logger.debug(f"Pydantic validation passed for booking ID: {validated.bookingid}")

        booking_id = result["bookingid"]
        created_ids.append(booking_id)
        logger.info(f"Factory created booking ID: {booking_id}")
        return result, booking_id

    yield _make_booking

    for booking_id in created_ids:
        _cleanup_booking(booking_client, booking_id, auth_token)


@pytest.fixture
def create_booking(booking_client, auth_token, booking_data):
    """Create a booking with retry and clean it up after the test.

    Validates the response against the Pydantic BookingResponse model.

    Yields:
        Tuple of (response_data, booking_id).
    """
    result = _create_booking_with_retry(booking_client, booking_data)

    _validate_booking_response(result)

    booking_id = result["bookingid"]
    logger.info(f"Created booking with ID: {booking_id}")

    yield result, booking_id

    _cleanup_booking(booking_client, booking_id, auth_token)
