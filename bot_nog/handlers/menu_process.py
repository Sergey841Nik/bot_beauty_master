from aiogram.types import InputMediaPhoto
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from databases.orm_query import orm_get_banner, orm_get_day_hour_records, orm_get_products, orm_get_records_user
from util.paginator import Paginator

from kbds.inline import (
    get_products_btns,
    get_user_calendar_btns,
    get_user_database_btns,
    get_user_hors_btns,
    get_user_main_btns,
    get_user_records_btns,
)


async def main_menu(session, level, menu_name):
    banner = await orm_get_banner(session, level=menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbds = get_user_main_btns(level=level)
    return image, kbds


async def calendar_menu(session, level, month_change, menu_name):
    banner = await orm_get_banner(session, level=menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbds = get_user_calendar_btns(level=level, month_change=month_change)
    return image, kbds


async def hors_menu(state, session, level, menu_name):
    date_ = await state.get_data()
    day = date_["day"]
    busy_time = await orm_get_day_hour_records(session, day)
    banner = await orm_get_banner(session, level=menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbds = get_user_hors_btns(level=level, busy_time=busy_time)
    return image, kbds


def pages(pagin: Paginator):
    btns = dict()
    if pagin.go_back():
        btns["Предыдущий ◀️"] = "back"
    if pagin.go_ahead():
        btns["Следующий ▶️"] = "forward"
    return btns


async def products(session, level, page):
    products = await orm_get_products(session)

    paginator = Paginator(products, page=page)
    product = paginator.get_page()[0]
    
    image = InputMediaPhoto(media=product.image, caption=f"<strong>{product.name}\
                </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}\n\
                <strong>Товар {paginator.page} из {paginator.pages}</strong>",
    )
    paginator_btns = pages(paginator)

    kbds = get_products_btns(
        level=level, page=page, paginator_btns=paginator_btns, product_id=product.id
    )

    return image, kbds


async def write_to_database(session, state, level, menu_name):
    date_ = await state.get_data()
    banner = await orm_get_banner(session, level=menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbds = get_user_database_btns(
        level=level,
        month_day=date_["day"],
        day_hours=date_["hour"],
    )
    return image, kbds

async def get_user_records(session, level, user_id, page):
    records = await orm_get_records_user(session, user_id)
    paginator = Paginator(records, page=page)
    record = paginator.get_page()[0]
    image = InputMediaPhoto(media=record.product.image, caption=f"Вы записаны на <strong>{record.day_hour}</strong>\n\
                            И выбрали {record.product.name}\n{record.product.description}\n\
                            Стоимость: {record.product.price}")
    kbds = get_user_records_btns(level=level, record_id=record.id)

    return image, kbds

#вызов разных функций в зависимости от уровня
async def get_menu_content(
    session: AsyncSession,
    state: FSMContext,
    menu_name: str,
    level: int,
    page: int = 1,
    user_id: int | None = None,
    month_change: int | None = None,
):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await calendar_menu(session, level, month_change, menu_name)
    elif level == 2:
        return await hors_menu(state, session, level, menu_name)
    elif level == 3:
        return await products(session, level, page)
    elif level == 4:
        return await write_to_database(session, state, level, menu_name)
    elif level == 5:
        return await get_user_records(session, level, user_id, page)
