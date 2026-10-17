import allure
import pytest
from models.booking import BookingCreateResponse, Booking

@allure.feature("Booking API")
@allure.story("POST /booking")
class TestPostBooking:
    @allure.title("Создание бронирования с полными данными")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("smoke", "positive", "regression")
    def test_create_booking(self, created_booking: BookingCreateResponse, valid_booking_data: Booking):
        assert created_booking.booking == valid_booking_data, "Созданное бронирование не совпадает с отправленным"

    @allure.title("Создание бронирования только с обязательными полями")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positive", "minimal", "regression")
    def test_create_booking_minimal_data(self, api_manager, authorized_api_manager, minimal_booking_data: Booking):
        with allure.step("Отправить POST /booking без additionalneeds"):
            create_response = api_manager.booking_api.create_booking(minimal_booking_data)
        with allure.step("Проверить, что ответ содержит созданное бронирование"):
            created = BookingCreateResponse(**create_response.json())
            assert created.booking == minimal_booking_data, "Минимальное бронирование не совпадает"
        with allure.step("Удалить созданную запись (очистка)"):
            authorized_api_manager.booking_api.delete_booking(created.bookingid)

    @allure.title("Создание бронирования с разными вариантами additionalneeds")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positive", "additional-needs", "regression")
    @pytest.mark.parametrize("needs", ["Breakfast", "Parking", "WiFi", None])
    def test_create_booking_with_various_additional_needs(self, api_manager, authorized_api_manager, valid_booking_data: Booking, needs):
        with allure.step(f"Установить additionalneeds = {needs}"):
            # Используем копирование модели вместо мутации фикстуры
            booking_data = valid_booking_data.model_copy(update={"additionalneeds": needs})
        with allure.step("Отправить POST /booking"):
            create_response = api_manager.booking_api.create_booking(booking_data)
        with allure.step("Проверить, что additionalneeds сохранено корректно"):
            created = BookingCreateResponse(**create_response.json())
            assert created.booking.additionalneeds == needs, f"Ожидалось {needs}, получено {created.booking.additionalneeds}"
        with allure.step("Удалить созданную запись (очистка)"):
            authorized_api_manager.booking_api.delete_booking(created.bookingid)

@allure.feature("Booking API")
@allure.story("POST /booking (негативные)")
class TestPostBookingNegative:
    @allure.title("Создание с отсутствующими обязательными полями (только firstname)")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negative", "missing-field", "regression")
    def test_create_booking_missing_fields(self, api_manager):
        with allure.step("Отправить POST /booking только с firstname"):
            api_manager.booking_api.create_booking({"firstname": "John"}, expected_status=500)

    @allure.title("Создание с невалидным totalprice (строка вместо числа)")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negative", "invalid-type", "regression")
    def test_create_booking_invalid_totalprice(self, api_manager, authorized_api_manager):
        invalid_data = {
            "firstname": "John",
            "lastname": "Doe",
            "totalprice": "not_a_number",
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-08-01", "checkout": "2026-08-10"}
        }
        with allure.step("Отправить POST /booking с строкой в totalprice"):
            response = api_manager.booking_api.create_booking(invalid_data, expected_status=200)
        with allure.step("Проверить, что totalprice стал null или 0"):
            booking = response.json()['booking']
            assert booking['totalprice'] is None or booking['totalprice'] == 0, "totalprice должен быть null или 0"
        booking_id = response.json().get('bookingid')
        if booking_id:
            with allure.step("Удалить созданную запись (очистка)"):
                authorized_api_manager.booking_api.delete_booking(booking_id)

    @allure.title("Создание с лишним полем (extra_field)")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negative", "extra-field", "regression")
    def test_create_booking_extra_field(self, api_manager, authorized_api_manager, valid_booking_data: Booking):
        extra_data = valid_booking_data.model_dump(mode='json')
        extra_data['extra_field'] = 'should be ignored'
        with allure.step("Отправить POST /booking с дополнительным полем"):
            response = api_manager.booking_api.create_booking(extra_data, expected_status=200)
        with allure.step("Проверить, что лишнее поле игнорируется"):
            booking = response.json()['booking']
            assert 'extra_field' not in booking, "Лишнее поле не должно присутствовать в ответе"
        booking_id = response.json().get('bookingid')
        if booking_id:
            with allure.step("Удалить созданную запись (очистка)"):
                authorized_api_manager.booking_api.delete_booking(booking_id)