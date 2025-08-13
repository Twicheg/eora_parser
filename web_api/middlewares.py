from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

import uuid


class UuidCookies(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Установка uuid в куках для идентификации посетителя"""

        if not request.cookies.get('client_id'):
            response = await call_next(request)
            response.set_cookie('client_id', str(uuid.uuid4()), samesite='strict')
            return response

        response = await call_next(request)
        return response
