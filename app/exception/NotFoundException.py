class NotFoundException(Exception):
    """Raised when the user returns something not found"""
    def __init__(self, message):
        self.message = message