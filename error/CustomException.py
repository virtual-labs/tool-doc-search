
class CustomException(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


class BadRequestException(CustomException):
    def __init__(self, message):
        super().__init__(message, 400)


class NotFoundException(CustomException):
    def __init__(self, message):
        super().__init__(message, 404)
