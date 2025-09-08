import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException


def fail(status: int, message: str):
    raise HTTPException(status, message)


def configure_errors(app: FastAPI):
    @app.middleware("http")
    async def request_id(request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request, exc):
        return JSONResponse(
            {"error": {"message": str(exc.detail), "request_id": request.state.request_id}},
            status_code=exc.status_code,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        fields = [
            {"field": ".".join(map(str, e["loc"][1:])), "message": e["msg"]} for e in exc.errors()
        ]
        return JSONResponse(
            {
                "error": {
                    "message": "Check the highlighted fields",
                    "fields": fields,
                    "request_id": request.state.request_id,
                }
            },
            status_code=422,
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error(request, exc):
        return JSONResponse(
            {
                "error": {
                    "message": "This change conflicts with an existing record",
                    "request_id": request.state.request_id,
                }
            },
            status_code=409,
        )
