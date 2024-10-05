from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from databases.models import User, Products, Record, Banner


##################### Добавляем товары в БД #####################################


async def orm_add_products(session: AsyncSession, data: dict):
    obj = Products(
        name=data["name"],
        description=data["description"],
        price=data["price"],
        image=data["image"],
    )
    session.add(obj)
    await session.commit()


##################### Добавляем юзера в БД #####################################


async def orm_add_user(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(
                user_id=user_id, first_name=first_name, last_name=last_name, phone=phone
            )
        )
    await session.commit()


##################### Работа с записями в БД #####################################
async def orm_add_to_record(session: AsyncSession, user_id: int, product_id: int, day: str, hour: str):

    day_hour = datetime.strptime(day + " " + hour, "%d.%m.%Y %H.%M")
    obj = Record(user_id=user_id, day_hour=day_hour, product_id=product_id)
    session.add(obj)
    await session.commit()

async def orm_get_records_admin(session: AsyncSession, day: str | None = None):
    if day:
        query = select(Record).options(joinedload(Record.user)).where(Record.day == day)
        result = await session.execute(query)
        return result.scalars().all()
    else:
        query = select(Record).options(joinedload(Record.user))
        result = await session.execute(query)
        return result.scalars().all()
    
async def orm_get_records_user(session: AsyncSession, user_id: int):
    query = select(Record).where(Record.user_id == user_id).options(joinedload(Record.product))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_day_hour_records(session: AsyncSession, day: str):
    day_to_datetime = datetime.strptime(day + " " + "00.00.00", "%d.%m.%Y %H.%M.%S")
    query = select(Record.day_hour)
    result = await session.execute(query)
    # for busy in result.scalars().all():
    #     if busy.date() == day_to_datetime.date():
    return [
        str(busy.time())[:-3].replace(":", ".")
        for busy in result.scalars().all()
        if busy.date() == day_to_datetime.date()
    ]
    # return result.scalars().all()


async def orm_delete_records_auto(session: AsyncSession):
    data_now = datetime.now()
    query = delete(Record).filter(Record.day_hour < data_now)
    await session.execute(query)
    await session.commit()


async def orm_delete_record(session: AsyncSession, record_id: int):
    query = delete(Record).filter(Record.id == record_id)
    await session.execute(query)
    await session.commit()

##################### Работа с товарами из БД #####################################


async def orm_get_products(session: AsyncSession):
    query = select(Products)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_products(session: AsyncSession, product_id: int):
    query = delete(Products).filter(Products.id == product_id)
    await session.execute(query)
    await session.commit()

############### Работа с баннерами (информационными страницами) из БД ###############

async def orm_add_banner(session: AsyncSession, data: dict):
    #Добавляем новый или изменяем существующий по именам
    #пунктов меню: start, calendar, hour, records
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()]) 
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, level: str):
    query = select(Banner).where(Banner.name == level)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_level(session: AsyncSession):
    query = select(Banner.name)
    result = await session.execute(query)
    return result.scalars().all()



