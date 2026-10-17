import allure
from custom_requester.custom_requester import CustomRequester
from config.settings import BASE_URL

class BookingApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=BASE_URL)

    @allure.step("Получение всех бронирований")
    def get_all_bookings(self, params=None, expected_status=200):
        return self.send_request('GET', '/booking', params=params, expected_status=expected_status)

    @allure.step("Получение бронирования по ID:{booking_id}")
    def get_booking_by_id(self, booking_id, expected_status=200):
        return self.send_request('GET', f'/booking/{booking_id}', expected_status=expected_status)

    @allure.step("Создание бронирования")
    def create_booking(self, booking_data, expected_status=200):
        return self.send_request('POST', '/booking', data=booking_data, expected_status=expected_status)

    @allure.step("Частичное обновление бронирования по ID:{booking_id}")
    def partial_update_booking(self, booking_id, update_data, expected_status=200):
        return self.send_request('PATCH', f'/booking/{booking_id}', data=update_data, expected_status=expected_status)

    @allure.step("Полное обновление бронирования по ID:{booking_id}")
    def update_booking(self, booking_id, update_data, expected_status=200):
        return self.send_request('PUT', f'/booking/{booking_id}', data=update_data, expected_status=expected_status)

    @allure.step("Удаление бронирования по ID:{booking_id}")
    def delete_booking(self, booking_id, expected_status=201):
        return self.send_request('DELETE', f'/booking/{booking_id}', expected_status=expected_status)

    @allure.step("Авторизация")
    def authenticate(self, admin_creds, expected_status=200):
        return self.send_request('POST', '/auth', data=admin_creds, expected_status=expected_status)