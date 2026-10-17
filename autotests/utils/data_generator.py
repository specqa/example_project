from typing import Optional
from faker import Faker
from datetime import timedelta
import random
from models.booking import BookingDates, Booking

faker = Faker()

class DataGenerator:

    @staticmethod
    def generate_random_firstname():
        return faker.first_name()

    @staticmethod
    def generate_random_lastname():
        return faker.last_name()

    @staticmethod
    def generate_random_totalprice():
        return faker.random_int(min=0, max=1000)

    @staticmethod
    def generate_random_depositpaid_status():
        return faker.boolean()

    def generate_booking_dates(min_days=1, max_days=30) -> BookingDates:
        checkin = faker.date_between(start_date='-30d', end_date='+60d')
        stay_duration = random.randint(min_days, max_days)
        checkout = checkin + timedelta(days=stay_duration)
        return BookingDates(checkin=checkin, checkout=checkout)

    @staticmethod
    def generate_additional_needs() -> Optional[str]:
        options = ["Breakfast", "Parking", "WiFi", "Pet friendly", "Late checkout", "Extra bed", None]
        return random.choice(options)

    @staticmethod
    def generate_booking_data() -> Booking:
        return Booking(
            firstname=faker.first_name(),
            lastname=faker.last_name(),
            totalprice=faker.random_int(min=0, max=1000),
            depositpaid=faker.boolean(),
            bookingdates=DataGenerator.generate_booking_dates(),
            additionalneeds=DataGenerator.generate_additional_needs()
        )

