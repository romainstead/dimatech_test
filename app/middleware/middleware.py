from sanic import Request, HTTPResponse

from app.database import async_session_maker


async def inject_session(request: Request):
    request.ctx.session = async_session_maker()


async def close_session(request: Request, response: HTTPResponse):
    if hasattr(request.ctx, "session"):
        await request.ctx.session.close()
