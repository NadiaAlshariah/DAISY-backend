class BadRequestException(Exception):
    """Raised when the user makes an invalid request."""
    def __init__(self, message):
        self.message = message