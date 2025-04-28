from datetime import date
from typing import Dict

from aiogram.filters.state import State, StatesGroup
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Calendar, CalendarScope
from aiogram_dialog.widgets.kbd.calendar_kbd import (CalendarDaysView,
                                                     CalendarMonthView,
                                                     CalendarScopeView,
                                                     CalendarYearsView)
from aiogram_dialog.widgets.text import Format, Text
from babel.dates import get_day_names, get_month_names

SELECTED_DAYS_KEY = 'selected_dates'


class CalendarState(StatesGroup):
    MAIN = State()
    DEFAULT = State()
    CUSTOM = State()


class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data['date']
        locale = manager.event.from_user.language_code
        return get_day_names(
            width='short', context='stand-alone', locale=locale,
        )[selected_date.weekday()].title()


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data['date']
        locale = manager.event.from_user.language_code
        return get_month_names(
            'wide', context='stand-alone', locale=locale,
        )[selected_date.month].title()


class CustomCalendar(Calendar):
    def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                header_text='🗓 ' + Month() + Format(' {date:%Y}'),
                weekday_text=WeekDay(),
                next_month_text=Month() + ' >>',
                prev_month_text='<< ' + Month(),
                config=self.config
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text='🗓 ' + Format('{date:%Y}'),
                this_month_text='[' + Month() + ']',
                config=self.config
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
                config=self.config
            ),
        }


async def on_date_clicked(callback, widget, manager, selected_date, /):
    await callback.answer(str(selected_date))


async def on_date_selected(callback, widget,  manager, clicked_date, /):
    selected = manager.dialog_data.setdefault(SELECTED_DAYS_KEY, [])
    serial_date = clicked_date.isoformat()
    if serial_date in selected:
        selected.remove(serial_date)
    else:
        selected.append(serial_date)


async def selection_getter(dialog_manager, **_):
    selected = dialog_manager.dialog_data.get(SELECTED_DAYS_KEY, [])
    return {'selected': ', '.join(sorted(selected)),}
