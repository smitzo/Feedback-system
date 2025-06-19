from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

def http_exception(status_code: int, detail: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail=detail)

def server_error(detail: str = "Internal server error") -> HTTPException:
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

def conflict_error(detail: str = "Resource conflict") -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

def not_found_error(detail: str = "Resource not found") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

def bad_request_error(detail: str = "Bad request") -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

def unauthorized_error(detail: str = "Unauthorized access") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
