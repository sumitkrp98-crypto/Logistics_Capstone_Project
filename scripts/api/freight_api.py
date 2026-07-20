import random
import time

# Exchange rates
EXCHANGE_RATES = {
    "INR": 85.0,
    "USD": 1.0,
    "EUR": 98.0
}

# Fuel surcharge percentage
FUEL_SURCHARGE = 0.08


def get_freight_rate(currency_code):
    """
    Mock Freight Rate API
    """

    # Simulate API failure
    if random.random() < 0.10:
        raise Exception("API temporarily unavailable")

    currency = currency_code.upper()

    # Missing exchange rate
    if currency not in EXCHANGE_RATES:
        return None

    return EXCHANGE_RATES[currency]


def get_rate_with_retry(currency_code, retries=3):

    for attempt in range(retries):

        try:
            rate = get_freight_rate(currency_code)

            if rate is not None:
                return rate

        except Exception:
            time.sleep(1)

    # Fallback
    return EXCHANGE_RATES["INR"]


def apply_fuel_surcharge(cost):

    return round(cost * (1 + FUEL_SURCHARGE), 2)