#Чат позвотеля. Реализовани с помощью фабрики коллбеков

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from databases.orm_query import orm_add_user, orm_add_to_record, orm_delete_record
from kbds.inline import MenuCallBack
from filter.chat_type import ChatTypeFilter
from handlers.menu_process import get_menu_content


user_privat_router = Router()
user_privat_router.message.filter(ChatTypeFilter(["private"])) #фильтр для чата (какого он типа в данном случаее private)

#Команда "/start"для запуска меню
@user_privat_router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext, session: AsyncSession) -> None:
    media, reply_markup = await get_menu_content(
        level=0, state=state, session=session, menu_name="start"
    )
    # await message.answer(text=text, reply_markup=reply_markup)
    await message.answer_photo(
        media.media, caption=media.caption, reply_markup=reply_markup
    )

#Занесение информации о пользователе и времени его записи в БД
async def add_to_write_in_bd(
    callback: CallbackQuery, info_record: dict, session: AsyncSession
) -> None:
    user = callback.from_user

    await orm_add_user(
        session=session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    )
    try:
        await orm_add_to_record(
            session=session,
            user_id=user.id,
            day=info_record["day"],
            hour=info_record["hour"],
            product_id=info_record["product_id"],
        )
    except SQLAlchemyError: #исключение ошибки если запись уже есть
        await callback.answer(
            f"Что то пошло не так\nВозможно кто-то опередил Вас\nпопробуйте записатся на другое время\nили перезапустить бота (menu->/start)",
            show_alert=True,
        )
    else:
        await callback.answer(
            f"Вы записались на {info_record['day']} в {info_record['hour']}",
            show_alert=True,
        )
    

###########################################фабрика callbacks#########################################
@user_privat_router.callback_query(MenuCallBack.filter())
async def user_menu(
    callback: CallbackQuery,
    callback_data: MenuCallBack,
    state: FSMContext,
    session: AsyncSession,
) -> None:
#обработка события при нажатии на пустую кнопку
    if callback_data.key_word == "busy":
        await callback.answer("Занято", show_alert=True)

    _dict_state = await state.get_data()

#обработка события при нажатии кнопки записи
    if callback_data.key_word == "record": 
        await add_to_write_in_bd(
            callback=callback, info_record=_dict_state, session=session
        )
        await state.clear()

#удаление записи пользователем из БД
    if callback_data.key_word == "delete": 
        await orm_delete_record(session, callback_data.product_id)

#сохранение данных для записи в БД
    if callback_data.month_day != None:                     
        await state.update_data(day=callback_data.month_day)
    if callback_data.day_hours != None:
        await state.update_data(hour=callback_data.day_hours)
    if callback_data.product_id != None:
        await state.update_data(product_id=callback_data.product_id)

# получение картики и кнопок от разных уровней(level) меню
    media, reply_markup = await get_menu_content(
        session,
        state,
        menu_name=callback_data.menu_name,
        level=callback_data.level,
        month_change=callback_data.month_change,
        page=callback_data.page,
        user_id=callback.from_user.id,
    )

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()
