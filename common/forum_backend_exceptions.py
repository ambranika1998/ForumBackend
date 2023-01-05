class ForumBackendException(BaseException):
    status_code = None
    message = None

    def __init__(self, status_code, message):
        super()
        self.status_code = status_code
        self.message = message
