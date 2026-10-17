import pytest
import requests
from clients.api_manager import ApiManager
from models.booking import Booking, BookingCreateResponse
from utils.data_generator import DataGenerator
from config.settings import ADMIN_CREDS
from models.booking import AuthRequest, AuthResponse

@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def auth_token(api_manager) -> str:
    auth_data = AuthRequest(**ADMIN_CREDS)
    response = api_manager.booking_api.authenticate(auth_data)
    auth_resp = AuthResponse(**response.json())
    return auth_resp.token

@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)

@pytest.fixture(scope="function")
def auth_session(auth_token):
    http_session = requests.Session()
    http_session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={auth_token}"
    })
    return http_session

@pytest.fixture
def authorized_api_manager(auth_session):
    return ApiManager(auth_session)

@pytest.fixture
def created_booking(api_manager, authorized_api_manager, valid_booking_data) -> BookingCreateResponse:
    response = api_manager.booking_api.create_booking(valid_booking_data)
    booking = BookingCreateResponse(**response.json())
    yield booking
    try:
        authorized_api_manager.booking_api.delete_booking(booking.bookingid)
    except Exception:
        pass

@pytest.fixture
def valid_booking_data() -> Booking:
    return DataGenerator.generate_booking_data()

@pytest.fixture
def minimal_booking_data() -> Booking:
    return Booking(
        firstname=DataGenerator.generate_random_firstname(),
        lastname=DataGenerator.generate_random_lastname(),
        totalprice=DataGenerator.generate_random_totalprice(),
        depositpaid=DataGenerator.generate_random_depositpaid_status(),
        bookingdates=DataGenerator.generate_booking_dates()
    )

@pytest.fixture
def update_data():
    return DataGenerator.generate_booking_data()