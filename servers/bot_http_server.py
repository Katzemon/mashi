import uvicorn
from fastapi import FastAPI
from starlette.datastructures import URL
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from configs.config import HTTP_PORT


class HttpsRedirectMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in ("http", "websocket") and scope["scheme"] in ("http", "ws"):
            url = URL(scope=scope)
            redirect_scheme = {"http": "https", "ws": "wss"}[url.scheme]
            url = url.replace(scheme=redirect_scheme, port=443)
            response = RedirectResponse(url, status_code=307)
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)


http_app = FastAPI()
http_app.add_middleware(HttpsRedirectMiddleware)

def start_http_server():
    uvicorn.run(http_app, host="0.0.0.0", port=HTTP_PORT)
