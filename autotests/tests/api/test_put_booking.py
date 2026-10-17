import allure
from models.booking import BookingCreateResponse, Booking

@allure.feature("Booking API")
@allure.story("PUT /booking/{id}")
class TestPutBookingPositive:
    @allure.title("Полное обновление бронирования (замена всех полей)")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("smoke", "positive", "put", "regression")
    def test_update_booking_full(self, authorized_api_manager, created_booking: BookingCreateResponse, update_data):
        booking_id = created_booking.bookingid
        with allure.step(f"Отправить PUT /booking/{booking_id} с новыми данными"):
            response = authorized_api_manager.booking_api.update_booking(booking_id, update_data, expected_status=200)
        with allure.step("Проверить, что все поля обновлены"):
            updated = Booking(**response.json())
            assert updated == update_data, "Обновлённые данные не совпадают"

@allure.feature("Booking API")
@allure.story("PUT /booking/{id} (негативные)")
class TestPutBookingNegative:
    @allure.title("Обновление без авторизации")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negative", "auth", "regression")
    def test_put_booking_without_auth(self, api_manager, created_booking: BookingCreateResponse):
        booking_id = created_booking.bookingid
        with allure.step("Отправить PUT /booking без токена"):
            api_manager.booking_api.update_booking(booking_id, {"firstname": "Hacker"}, expected_status=403)

    @allure.title("Обновление несуществующего бронирования")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negative", "not-found", "regression")
    def test_put_booking_not_found(self, authorized_api_manager):
        with allure.step("Отправить PUT /booking/999999"):
            authorized_api_manager.booking_api.update_booking(999999, {"firstname": "Ghost"}, expected_status=400)

    @allure.title("Обновление с отсутствующим обязательным полем")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negative", "missing-field", "regression")
    def test_put_booking_missing_field(self, authorized_api_manager, created_booking: BookingCreateResponse, update_data):
        booking_id = created_booking.bookingid
        data = update_data.model_dump(mode='json')
        del data['firstname']
        with allure.step("Отправить PUT /booking без поля firstname"):
            authorized_api_manager.booking_api.update_booking(booking_id, data, expected_status=400)