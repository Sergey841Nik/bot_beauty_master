import calendar
from datetime import date
from sys import prefix

from aiogram.filters.callback_data import CallbackData

DAYS_WEEK = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")

MONTH_YEAR = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}

class CalendarForInline:
    def __init__(self):
        self.__month = date.today().month
        self.__year = date.today().year

    def month_plus_minus(self, delta):
        self.__month += delta
    
    
    def month_select(self):
        if self.__month > 12:
            self.__month = 1
            self.__year += 1
            return self.__year, self.__month
        elif self.__month < 1:
            self.__month = 12
            self.__year -= 1
            return self.__year, self.__month
        else:
            return self.__year, self.__month
        
    def list_month_days(self):
        func_calendar = calendar.Calendar()
        days_month_int = func_calendar.itermonthdays(self.month_select()[0], self.month_select()[1])
        days_month_str = []
        for day in days_month_int:
            if day != 0 and date(self.__year, self.__month, day) >= date.today():
                days_month_str.append(str(day))
            else:
                days_month_str.append(' ') 
        return days_month_str
    

if __name__ == '__main__':
    m = CalendarForInline()
    print(m.list_month_days())