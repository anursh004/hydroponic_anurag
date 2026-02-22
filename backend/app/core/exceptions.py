from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int = 500,
        detail: str = "Internal server error",
        error_code: str = "INTERNAL_ERROR",
    ):
        self.error_code = error_code
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(status_code=404, detail=detail, error_code=error_code)


class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request", error_code: str = "BAD_REQUEST"):
        super().__init__(status_code=400, detail=detail, error_code=error_code)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Not authenticated", error_code: str = "UNAUTHORIZED"):
        super().__init__(status_code=401, detail=detail, error_code=error_code)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Not enough permissions", error_code: str = "FORBIDDEN"):
        super().__init__(status_code=403, detail=detail, error_code=error_code)


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists", error_code: str = "CONFLICT"):
        super().__init__(status_code=409, detail=detail, error_code=error_code)


class ValidationException(AppException):
    def __init__(self, detail: str = "Validation error", error_code: str = "VALIDATION_ERROR"):
        super().__init__(status_code=422, detail=detail, error_code=error_code)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
        },
    )
