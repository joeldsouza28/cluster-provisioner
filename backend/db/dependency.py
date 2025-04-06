from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request



async def get_db_connection(request: Request):

    session: AsyncSession = request.app.state.db_session_factory()

    try:
        yield session
    finally:
        await session.commit()
        await session.close()