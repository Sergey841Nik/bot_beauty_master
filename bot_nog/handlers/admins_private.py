from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from databases.orm_query import (
    orm_change_banner_image,
    orm_get_info_level,
    orm_get_products,
    orm_add_products,
    orm_get_records_admin,
    orm_delete_record,
    orm_delete_products,
    orm_delete_records_auto
)
from filter.chat_type import ChatTypeFilter, IsAdmin
from kbds.inline import get_btns
from kbds.repley import get_kyboard

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = get_kyboard(
    "Добавить товар",
    "Товары",
    "Посмотреть все записи",
    "Добавить/Изменить банер",
    placeholder="Выберите действие",
)


@admin_router.message(Command("admin"))
async def admin_start(message: Message, session: AsyncSession):
    await orm_delete_records_auto(session)
    await message.answer(
        " Вы вошли как админ. Что хотите сделать?", reply_markup=ADMIN_KB
    )


##################################Работа с записями клиентов##################################################


@admin_router.message((F.text.lower() == "посмотреть все записи"))
async def look_all_recod(message: Message, session: AsyncSession):

    for rec in await orm_get_records_admin(session):
        await message.answer(
            f"Запись {rec.user.first_name} на {rec.day_hour.day}.{rec.day_hour.month}.{rec.day_hour.year} время {rec.day_hour.time()}",
            reply_markup=get_btns(btn={"Удалиь запись": f"delete_rec_{rec.id}"}),
        )


@admin_router.callback_query(F.data.startswith("delete_rec_"))
async def delete_record(callback: CallbackQuery, session: AsyncSession):

    record_id = int(callback.data.split("_")[-1])
    await orm_delete_record(session, record_id)
    await callback.answer("Запись удалена")
    await callback.message.answer("Запись удалена")


##################################Раобота с продуктами#########################################################
@admin_router.message((F.text == "Товары"))
async def look_all_products(message: Message, session: AsyncSession):
    print(message.from_user.first_name)
    for product in await orm_get_products(session):
        await message.answer_photo(
            product.image,
            caption=f"<strong>{product.name} </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}",
            reply_markup=get_btns(
                btn={
                    "Удалить товар": f"delete_product_{product.id}",
                    "Измениь товар": f"cheng_{product.id}",
                }
            ),
        )


@admin_router.callback_query(F.data.startswith("delete_product_"))
async def delete_products(callback: CallbackQuery, session: AsyncSession):

    product_id = int(callback.data.split("_")[-1])
    await orm_delete_products(session, product_id)
    await callback.answer("Товар удален")
    await callback.message.answer("Товар удален")


###################################FSM машина для добовления товаров##########################################


class AdminState(StatesGroup):
    # Контекст для состояния(шаги состояния)
    name = State()
    description = State()
    price = State()
    image = State()
    texts = {   #для реализации шага назад, чтобы знать где находимся и какой предыдущий шаг
        "AdminState:name": "Введите название заново:",
        "AdminState:description": "Введите описание заново:",
        "AdminState:price": "Введите стоимость заново:",
        "AdminState:image": "Этот стейт последний, поэтому...",
    }

#ловим нажатие кнопрки "добавить товар" и становимся в ожидание ввода названия name
@admin_router.message(StateFilter(None), (F.text.lower() == "добавить товар"))
async def add_product(message: Message, state: FSMContext):
    await message.answer("Введите название", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminState.name)

#реализуем ввод отмены
#и очищаем state (это фактически словарь в котором сохроняються введённые состояния)
@admin_router.message(StateFilter("*"), Command("отмена"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel(message: Message, state: FSMContext):
    curent_state = await state.get_state()
    if curent_state is None:
        return
    await state.clear()
    await message.answer("Отмена", reply_markup=ADMIN_KB)

#реализуем ввод назад
@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AdminState.name:
        await message.answer(
            'Предыдущего шага нет, или введите название товара или напишите "отмена"'
        )
        return

    previous = None
    for step in AdminState.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AdminState.texts[previous.state]}"
            )
            return
        previous = step

#ловим введённое название и ждём введение описания и добовляем инфу в state
@admin_router.message(AdminState.name, F.text)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание")
    await state.set_state(AdminState.description)

#аналогично
@admin_router.message(AdminState.description, F.text)
async def add_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите стоимость")
    await state.set_state(AdminState.price)


@admin_router.message(AdminState.price, F.text)
async def add_prise(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Загрузите изображение товара")
    await state.set_state(AdminState.image)

#ловим фото и получем из state словарь котрый и передём в ORM для добавления в БД
@admin_router.message(AdminState.image, F.photo)
async def add_prise(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(image=message.photo[-1].file_id)
    await message.answer("Товар добавлен", reply_markup=ADMIN_KB)
    data = await state.get_data()
    try:
        await orm_add_products(session, data)
        await session.commit()
        await message.answer(str(data))
        await state.clear()
    except Exception as e:
        await message.answer(
            text=f"Произошла ошибка {e},\nобратитесь к програмисут",
            reply_markup=ADMIN_KB,
        )


################# FSM для загрузки/изменения баннеров ############################

class AddBanner(StatesGroup):
    image = State()

# Отправляем перечень информационных страниц бота и становимся в состояние отправки photo
@admin_router.message(StateFilter(None), F.text == 'Добавить/Изменить банер')
async def add_image2(message: Message, state: FSMContext, session: AsyncSession):
    level_names = [level for level in await orm_get_info_level(session)]
    await message.answer(f"Отправьте фото баннера.\nВ описании укажите для какой страницы:\
                         \n{', '.join(level_names)}")
    await state.set_state(AddBanner.image)

# Добавляем/изменяем изображение в таблице (там уже есть записанные страницы по именам:
# main, catalog, cart(для пустой корзины), about, payment, shipping
@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    level_names = [level for level in await orm_get_info_level(session)]
    if for_page not in level_names:
        await message.answer(f"Введите нормальное название страницы, например:\
                         \n{', '.join(level_names)}")
        return
    await orm_change_banner_image(session, for_page, image_id,)
    await message.answer("Баннер добавлен/изменен.")
    await state.clear()

# ловим некоррекный ввод
@admin_router.message(AddBanner.image)
async def add_banner2(message: Message, state: FSMContext):
    await message.answer("Отправьте фото баннера или отмена")

#########################################################################################