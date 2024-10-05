from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from sqlalchemy.ext.asyncio import async_sessionmaker

#создаём Middleware слои для работы с базой данных

class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool  #создаём сессию при регистрации слоя (передаём сюда session_maker)


    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],  
        event: TelegramObject,                                                  #тип событий на которые навешивается сессия
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)                 #по параметру sesioin передаётся session_maker из файла engine.py