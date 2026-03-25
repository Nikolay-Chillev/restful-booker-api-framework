import allure
import pytest

from utils.helpers import generate_booking_data


@allure.epic("Booking API")
@allure.feature("E2E Workflows")
class TestBookingWorkflow:
    """End-to-end workflow tests covering full booking lifecycle."""

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Full booking lifecycle: Create -> Get -> Update -> Partial Update -> Delete")
    @pytest.mark.e2e
    @pytest.mark.smoke
    def test_full_booking_lifecycle(self, booking_client, auth_token):
        """Verify the complete booking lifecycle from creation to deletion."""

        # Step 1: Create booking
        booking_data = generate_booking_data()
        with allure.step("Step 1: Create a new booking"):
            create_response = booking_client.create_booking(booking_data)
            assert create_response.status_code == 200
            created = create_response.json()
            booking_id = created["bookingid"]
            assert booking_id is not None
            allure.attach(str(booking_id), name="Created Booking ID")

        # Step 2: Get and verify
        with allure.step("Step 2: Get the created booking and verify data"):
            get_response = booking_client.get_booking(booking_id)
            assert get_response.status_code == 200
            data = get_response.json()
            assert data["firstname"] == booking_data["firstname"]
            assert data["lastname"] == booking_data["lastname"]

        # Step 3: Full update (PUT)
        updated_data = generate_booking_data()
        with allure.step("Step 3: Full update the booking (PUT)"):
            update_response = booking_client.update_booking(
                booking_id, updated_data, auth_token
            )
            assert update_response.status_code == 200
            updated = update_response.json()
            assert updated["firstname"] == updated_data["firstname"]

        # Step 4: Partial update (PATCH)
        with allure.step("Step 4: Partial update the booking (PATCH)"):
            patch_response = booking_client.partial_update_booking(
                booking_id, {"firstname": "PatchedName", "totalprice": 1234}, auth_token
            )
            assert patch_response.status_code == 200
            patched = patch_response.json()
            assert patched["firstname"] == "PatchedName"
            assert patched["totalprice"] == 1234
            # Verify unchanged fields
            assert patched["lastname"] == updated_data["lastname"]

        # Step 5: Delete
        with allure.step("Step 5: Delete the booking"):
            delete_response = booking_client.delete_booking(booking_id, auth_token)
            assert delete_response.status_code == 201

        # Step 6: Verify deleted
        with allure.step("Step 6: Verify booking is deleted (GET returns 404)"):
            get_deleted = booking_client.get_booking(booking_id)
            assert get_deleted.status_code == 404

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Search workflow: Create multiple bookings and filter")
    @pytest.mark.e2e
    def test_search_workflow(self, booking_client, auth_token):
        """Create multiple bookings and verify search/filter functionality."""
        unique_name = "SearchTestUser"
        created_ids = []

        with allure.step("Create 3 bookings with same firstname"):
            for i in range(3):
                data = generate_booking_data()
                data["firstname"] = unique_name
                response = booking_client.create_booking(data)
                assert response.status_code == 200
                created_ids.append(response.json()["bookingid"])

        with allure.step(f"Search bookings by firstname={unique_name}"):
            ids = booking_client.get_booking_ids(params={"firstname": unique_name})
            found_ids = [item["bookingid"] for item in ids]

        with allure.step("Verify all created bookings are found"):
            for booking_id in created_ids:
                assert booking_id in found_ids, f"Booking {booking_id} not found in search results"

        with allure.step("Cleanup: delete all created bookings"):
            for booking_id in created_ids:
                booking_client.delete_booking(booking_id, auth_token)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Rapid update: Create and immediately update booking")
    @pytest.mark.e2e
    def test_rapid_create_and_update(self, booking_client, auth_token):
        """Create a booking and immediately update it to verify consistency."""

        with allure.step("Create booking"):
            data = generate_booking_data()
            create_response = booking_client.create_booking(data)
            assert create_response.status_code == 200
            booking_id = create_response.json()["bookingid"]

        with allure.step("Immediately update the booking"):
            new_data = generate_booking_data()
            update_response = booking_client.update_booking(
                booking_id, new_data, auth_token
            )
            assert update_response.status_code == 200

        with allure.step("Verify the latest state reflects the update"):
            get_response = booking_client.get_booking(booking_id)
            final = get_response.json()
            assert final["firstname"] == new_data["firstname"]
            assert final["lastname"] == new_data["lastname"]
            assert final["totalprice"] == new_data["totalprice"]

        with allure.step("Cleanup"):
            booking_client.delete_booking(booking_id, auth_token)
