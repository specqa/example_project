import allure
import pytest
from models.booking import Booking, BookingCreateResponse

@allure.feature("Booking API")
@allure.story("PATCH /booking/{id}")
class TestPatchBookingPositive:
    @allure.title("Частичное обновление одного поля")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positive", "patch", "regression")
    @pytest.mark.parametrize("field, value", [
        ("firstname", "NewName"),
        ("lastname", "NewLastName"),
        ("totalprice", 999),
        ("depositpaid", True),
        ("additionalneeds", "Dinner")
    ])
    def test_update_booking_partial_field(self, authorized_api_manager, created_booking: BookingCreateResponse, field, value):
        booking_id = created_booking.bookingid
        with allure.step(f"Отправить PATCH /booking/{booking_id} с полем {field}={value}"):
            response = authorized_api_manager.booking_api.partial_update_booking(booking_id, {field: value}, expected_status=200)
        with allure.step("Проверить, что поле обновлено"):
            updated = Booking(**response.json())
            assert getattr(updated, field) == value, f"Поле {field} не обновлено"

    @allure.title("Обновление только дат бронирования")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positive", "patch", "dates", "regression")
    def test_update_booking_partial_dates(self, authorized_api_manager, created_booking: BookingCreateResponse):
        booking_id = created_booking.bookingid
        new_dates = {
            "bookingdates": {
                "checkin": "2026-08-01",
                "checkout": "2026-08-10"
            }
        }
        with allure.step(f"Отправить PATCH /booking/{booking_id} с новыми датами"):
            response = authorized_api_manager.booking_api.partial_update_booking(booking_id, new_dates, expected_status=200)
        with allure.step("Проверить, что даты обновились"):
            updated = Booking(**response.json())
            assert updated.bookingdates.checkin.isoformat() == "2026-08-01", "checkin не обновлён"
            assert updated.bookingdates.checkout.isoformat() == "2026-08-10", "checkout не обновлён"

    @allure.title("Обновление нескольких полей одновременно")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positive", "patch", "multiple", "regression")
    def test_update_booking_multiple_fields(self, authorized_api_manager, created_booking: BookingCreateResponse):
        booking_id = created_booking.bookingid
        update_data = {
            "firstname": "Alice",
            "lastname": "Wonderland",
            "additionalneeds": "Tea"
        }
        with allure.step(f"Отправить PATCH /booking/{booking_id} с несколькими полями"):
            response = authorized_api_manager.booking_api.partial_update_booking(booking_id, update_data, expected_status=200)
        with allure.step("Проверить, что все поля обновлены"):
            updated = Booking(**response.json())
            assert updated.firstname == "Alice", "firstname не обновлён"
            assert updated.lastname == "Wonderland", "lastname не обновлён"
            assert updated.additionalneeds == "Tea", "additionalneeds не обновлён"

@allure.feature("Booking API")
@allure.story("PATCH /booking/{id} (негативные)")
class TestPatchBookingNegative:
    @allure.title("Обновление без авторизации")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negative", "auth", "regression")
    def test_patch_booking_without_auth(self, api_manager, created_booking: BookingCreateResponse):
        booking_id = created_booking.bookingid
        with allure.step("Отправить PATCH /booking без токена"):
            api_manager.booking_api.partial_update_booking(booking_id, {"firstname": "Hacker"}, expected_status=403)

    @allure.title("Обновление несуществующего бронирования")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negative", "not-found", "regression")
    def test_patch_booking_not_found(self, authorized_api_manager):
        with allure.step("Отправить PATCH /booking/999999"):
            authorized_api_manager.booking_api.partial_update_booking(999999, {"firstname": "Ghost"}, expected_status=405)

    @allure.title("Пустое тело запроса (без изменений)")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negative", "empty-body", "regression")
    def test_patch_booking_empty_body(self, authorized_api_manager, created_booking: BookingCreateResponse):
        booking_id = created_booking.bookingid
        with allure.step("Сохранить оригинальное бронирование"):
            original = created_booking.booking
        with allure.step("Отправить PATCH /booking с пустым телом"):
            response = authorized_api_manager.booking_api.partial_update_booking(booking_id, {}, expected_status=200)
        with allure.step("Проверить, что данные не изменились"):
            updated = Booking(**response.json())
            assert updated == original, "Данные изменились при пустом теле"