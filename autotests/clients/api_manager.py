from clients.booking_client import BookingApi

class ApiManager:
    def __init__(self, session):
        self.session = session
        self.booking_api = BookingApi(session)

    def close_session(self):
        if self.session:
            self.session.close()