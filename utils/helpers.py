import json
from datetime import timedelta
from pathlib import Path

import pytest
from faker import Faker

fake = Faker()

TEST_DATA_DIR = Path(__file__).parent.parent / "test_data"


def generate_booking_data() -> dict:
    """Generate random valid booking data using Faker."""
    checkin = fake.date_between(start_date="today", end_date="+30d")
    checkout = checkin + timedelta(days=fake.random_int(min=1, max=14))

    return {
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "totalprice": fake.random_int(min=50, max=1500),
        "depositpaid": fake.boolean(),
        "bookingdates": {
            "checkin": checkin.strftime("%Y-%m-%d"),
            "checkout": checkout.strftime("%Y-%m-%d"),
        },
        "additionalneeds": fake.random_element(
            ["Breakfast", "Lunch", "Dinner", "Parking", "Wi-Fi", "None"]
        ),
    }


def load_test_data(filename: str, id_func) -> list:
    """Load parametrized test data from a JSON file.

    Args:
        filename: JSON file name in test_data/ directory.
        id_func: Callable that takes an item and returns a string ID for pytest.param.

    Returns:
        List of pytest.param objects.
    """
    data_file = TEST_DATA_DIR / filename
    with open(data_file, "r") as f:
        items = json.load(f)
    return [pytest.param(item, id=id_func(item)) for item in items]
