# Package exports
# (C) Poren Chiang 2020

from .models import Weather, Provider
from .exceptions import WeatherParseError

def get():
    """Retrieves current weather information from the default provider."""
    from .providers import NTUSAProvider
    return NTUSAProvider().get()
