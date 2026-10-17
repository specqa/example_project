import allure
from models.booking import BookingCreateResponse

@allure.feature("Booking API")
@allure.story("DELETE /booking/{id}")
class TestDeleteBookingPositive:
    @allure.title("Удаление существующего бронирования")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("smoke", "positive", "delete", "regression")
    def test_delete_booking_success(self, authorized_api_manager, created_booking: BookingCreateResponse):
        booking_id = created_booking.bookingid
        with allure.step(f"Отправить DELETE /booking/{booking_id}"):
            authorized_api_manager.booking_api.delete_booking(booking_id)
        with allure.step("Проверить, что бронирование действительно удалено (GET возвращает 404)"):
            authorized_api_manager.booking_api.get_booking_by_id(booking_id, expected_status=404)

@allure.feature("Booking API")
@allure.story("DELETE /booking/{id} (негативные)")
class TestDeleteBookingNegative:
    @allure.title("Удаление без авторизации")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("negative", "auth", "regression")
    def test_delete_booking_without_auth(self, api_manager, created_booking: BookingCreateResponse):
        booking_id = created_booking.bookingid
        with allure.step("Отправить DELETE /booking без токена"):
            api_manager.booking_api.delete_booking(booking_id, expected_status=403)

    @allure.title("Удаление несуществующего бронирования")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negative", "not-found", "regression")
    def test_delete_booking_not_found(self, authorized_api_manager):
        with allure.step("Отправить DELETE /booking/999999"):
            authorized_api_manager.booking_api.delete_booking(999999, expected_status=405)

    @allure.title("Повторное удаление уже удалённого бронирования")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negative", "duplicate", "regression")
    def test_delete_booking_twice(self, authorized_api_manager, created_booking: BookingCreateResponse):
        booking_id = created_booking.bookingid
        with allure.step("Первое удаление"):
            authorized_api_manager.booking_api.delete_booking(booking_id)
        with allure.step("Второе удаление (ожидается 405 или 404)"):
            authorized_api_manager.booking_api.delete_booking(booking_id, expected_status=405)

    @allure.title("Удаление с невалидным форматом ID")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negative", "invalid-id", "regression")
    def test_delete_booking_invalid_id_format(self, authorized_api_manager):
        with allure.step("Отправить DELETE /booking/abc"):
            authorized_api_manager.booking_api.delete_booking("abc", expected_status=405)