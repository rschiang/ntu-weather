# Errors
# (C) Poren Chiang 2020

class WeatherParseError(ValueError):
    """Raised when the module failed to parse the source string."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.text = kwargs.get('text')
