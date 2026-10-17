import allure
import pytest
from models.booking import BookingCreateResponse, Booking, BookingListItem

@allure.feature("Booking API")
@allure.story("GET /booking")
class TestGetBookingPositive:
    @allure.title("Получение списка всех бронирований")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "positive", "regression")
    def test_get_all_bookings(self, api_manager):
        with allure.step("Отправить запрос GET /booking"):
            response = api_manager.booking_api.get_all_bookings()
        with allure.step("Проверить, что ответ является списком"):
            data = response.json()
            assert isinstance(data, list), "Ответ должен быть списком"
        with allure.step("Проверить, что список не пустой"):
            assert len(data) > 0, "Список бронирований пуст"
        with allure.step("Проверить структуру каждого элемента списка"):
            for item in data:
                booking_item = BookingListItem(**item)
                assert booking_item.bookingid > 0, "bookingid должен быть положительным числом"

    @allure.title("Получение бронирования по существующему ID")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("smoke", "positive", "regression")
    def test_get_booking_by_id(self, api_manager, created_booking: BookingCreateResponse):
        with allure.step("Получить ID созданного бронирования"):
            booking_id = created_booking.bookingid
            expected_booking = created_booking.booking
        with allure.step(f"Отправить GET /booking/{booking_id}"):
            response = api_manager.booking_api.get_booking_by_id(booking_id)
        with allure.step("Сравнить полученные данные с ожидаемыми"):
            actual_booking = Booking(**response.json())
            assert actual_booking == expected_booking, "Данные бронирования не совпадают"

    @allure.title("Фильтрация бронирований по имени")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positive", "filter", "regression")
    def test_get_bookings_with_filter_by_firstname(self, api_manager, created_booking: BookingCreateResponse):
        with allure.step("Получить firstname из созданного бронирования"):
            firstname = created_booking.booking.firstname
        with allure.step(f"Отправить GET /booking?firstname={firstname}"):
            response = api_manager.booking_api.get_all_bookings(params={"firstname": firstname})
        with allure.step("Проверить, что все найденные записи имеют такое же имя"):
            data = response.json()
            assert isinstance(data, list), "Ответ должен быть списком"
            assert len(data) > 0, "Не найдено бронирований с таким именем"
            for item in data:
                detail = api_manager.booking_api.get_booking_by_id(item["bookingid"]).json()
                assert detail["firstname"] == firstname, f"Имя в бронировании {item['bookingid']} не совпадает"

@allure.feature("Booking API")
@allure.story("GET /booking (негативные)")
class TestGetBookingNegative:
    @allure.title("Попытка получить бронирование по невалидному ID")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negative", "invalid-id", "regression")
    @pytest.mark.parametrize("invalid_id", [999999, -1, 0, "abc"])
    def test_get_booking_invalid_id(self, api_manager, invalid_id):
        with allure.step(f"Отправить GET /booking/{invalid_id} и ожидать статус 404"):
            api_manager.booking_api.get_booking_by_id(invalid_id, expected_status=404)

    @allure.title("Фильтрация с невалидными параметрами")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("negative", "filter", "regression")
    @pytest.mark.parametrize("filter_params, expected_status", [
        ({"firstname": "NonExistentName"}, 200),
        ({"checkin": "2020-01-01", "checkout": "2020-01-02"}, 200),
        ({"firstname": "John", "checkin": "invalid-date"}, 500)
    ])
    def test_get_bookings_with_invalid_filters(self, api_manager, filter_params, expected_status):
        with allure.step(f"Отправить GET /booking с параметрами {filter_params}"):
            response = api_manager.booking_api.get_all_bookings(params=filter_params, expected_status=expected_status)
        if expected_status == 200:
            with allure.step("Проверить, что ответ — список (скорее всего пустой)"):
                data = response.json()
                assert isinstance(data, list), "Ответ должен быть списком"
        else:
            with allure.step("Проверить, что статус 500 и текст содержит ошибку"):
                assert "Internal Server Error" in response.text or response.status_code == 500, "Ожидалась ошибка 500"