from typing import Any

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from util.calendar_list import DAYS_WEEK, MONTH_YEAR, CalendarForInline


class MenuCallBack(CallbackData, prefix="menu"):  #класс для фабрики Callback (что возвращает callback_data в inlain кнопке)
    level: int
    menu_name: str | None = None
    key_word: str | None = None
    month_day: str | None = None
    day_hours: str | None = None
    product_id: int | None = None
    page: int = 1
    month_change: int = 0


def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Календарь": "calendar",
        "Мои записи": "zapusi",
    }
    for text, menu_name in btns.items():
        if menu_name == "calendar":
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(
                        level=level + 1, menu_name=menu_name
                    ).pack(),
                )
            )
        elif menu_name == "zapusi":
            keyboard.add(
                InlineKeyboardButton(text=text, callback_data=MenuCallBack(
                        level=5, menu_name=menu_name
                    ).pack())
            )

    return keyboard.adjust(*sizes).as_markup()


def get_user_calendar_btns(
    *,
    level: int,
    month_change: int | None = None,
    sizes: tuple[int] = (
        1,
        1,
        2,
        7,
    ),
):
    calendar_ = CalendarForInline()
    calendar_.month_plus_minus(delta=month_change)
    month_ = MONTH_YEAR.get(calendar_.month_select()[1])
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(
            text="Назад",
            callback_data=MenuCallBack(level=level - 1, menu_name="start").pack(),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=month_, callback_data=MenuCallBack(level=level).pack()
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="<<",
            callback_data=MenuCallBack(
                level=1, menu_name="calendar", month_change=month_change - 1
            ).pack(),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=">>",
            callback_data=MenuCallBack(
                level=1, menu_name="calendar", month_change=month_change + 1
            ).pack(),
        )
    )
    for day_week in DAYS_WEEK:
        keyboard.add(
            InlineKeyboardButton(
                text=day_week, callback_data=MenuCallBack(level=level, menu_name="calendar").pack()
            )
        )
    for day_month in calendar_.list_month_days():
        keyboard.add(
            InlineKeyboardButton(
                text=day_month,
                callback_data=MenuCallBack(
                    level=level + 1,
                    menu_name="hour",
                    month_day=f"{day_month}.{calendar_.month_select()[1]}.{calendar_.month_select()[0]}",
                ).pack(),
            )
        )

    return keyboard.adjust(*sizes).as_markup()


def get_user_hors_btns(*, level: int, busy_time: list[str], sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    hours = ["08.00", "10.00", "12.00", "14.00", "16.00", "18.00", "20.00", "22.00"]

    if busy_time:
        for busy in busy_time:  # добовляем пустые конопки времени если они заняты
            index = hours.index(busy)
            hours[index] = " "

    for hour in hours:
        if hour == " ":
            keyboard.add(
                InlineKeyboardButton(
                    text=hour,
                    callback_data=MenuCallBack(
                        level=level, menu_name="hour", key_word='busy'
                    ).pack(),
                )
            )
        else:
            keyboard.add(
                InlineKeyboardButton(
                    text=hour,
                    callback_data=MenuCallBack(level=level + 1, day_hours=hour).pack(),
                )
            )
    keyboard.add(
        InlineKeyboardButton(
            text="Назад", callback_data=MenuCallBack(level=level - 1, menu_name='calendar').pack()
        )
    )

    return keyboard.adjust(*sizes).as_markup()


def get_products_btns(
    *,
    level: int,
    page: int,
    paginator_btns: dict,
    product_id: int,
    sizes: tuple[int] = (2, 1),
):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text="Назад", callback_data=MenuCallBack(level=level - 1, menu_name='hour').pack()
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="Выбрать",
            callback_data=MenuCallBack(level=level + 1, menu_name='records', product_id=product_id).pack(),
        )
    )
    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in paginator_btns.items():
        if menu_name == "forward":
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(
                        level=level, menu_name=menu_name, page=page + 1
                    ).pack(),
                )
            )
        elif menu_name == "back":
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(
                        level=level, menu_name=menu_name, page=page - 1
                    ).pack(),
                )
            )
    return keyboard.row(*row).as_markup()


def get_user_database_btns(
    *, level: int, month_day: str, day_hours: str, sizes: tuple[int] = (1,)
):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text=f"Записатся на {month_day} {day_hours}",
            callback_data=MenuCallBack(level=0, menu_name="start", key_word="record").pack(),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="Нет я не хочу на это время",
            callback_data=MenuCallBack(level=level - 3, menu_name='calendar').pack(),
        )
    )

    return keyboard.adjust(*sizes).as_markup()

def get_user_records_btns(*, level: int, record_id: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text="На стартовую",
            callback_data=MenuCallBack(level=0, menu_name="start").pack(),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="Ой, не хочу.../удалить",
            callback_data=MenuCallBack(level=0, menu_name='start', key_word='delete', product_id=record_id).pack(),
        )
    )
    return keyboard.adjust(*sizes).as_markup()




def get_btns(*, btn: dict[str, Any], sizes: tuple[int] = (2,)):

    keyboard = InlineKeyboardBuilder()
    for text, callback_data in btn.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    return keyboard.adjust(*sizes).as_markup()


