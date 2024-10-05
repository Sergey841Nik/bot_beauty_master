import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from middlewere.db import DataBaseSession
from databases.engine import create_db, drop_db, session_maker
from commands.bot_cmds_list import privat
from handlers.user_privat import user_privat_router
from handlers.admins_private import admin_router

bot = Bot(token=os.getenv("TOKEN"), parse_mode=ParseMode.HTML)  #зауск бота 

dp = Dispatcher()

dp.include_router(user_privat_router)   #регистрация роутеров
dp.include_router(admin_router)


async def on_startup(bot): 

    # await drop_db()

    await create_db()


async def on_shutdown(bot):
    print("бот лег")

async def main():
    dp.startup.register(on_startup) #запускается при старте бота
    dp.shutdown.register(on_shutdown) #запускается при остановке бота
    
    dp.update.middleware(DataBaseSession(session_pool=session_maker)) 

    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(
        commands=privat, scope=types.BotCommandScopeAllPrivateChats()
    )
    await dp.start_polling(bot, polling_timeout=3, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
