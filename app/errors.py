from fastapi import HTTPException, status


"""
HTTP Exceptions.
"""


class Error400(HTTPException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=self.message)


class Error401(HTTPException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=self.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


class Error402(HTTPException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=self.message
        )


class Error403(HTTPException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=self.message)


class Error404(HTTPException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=self.message)


class Error405(HTTPException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=self.message
        )


class Error409(HTTPException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=self.message)


class Error422(HTTPException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=self.message
        )


class Error500(HTTPException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=self.message
        )


class Error501(HTTPException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=self.message
        )
