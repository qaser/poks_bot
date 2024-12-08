from aiogram.filters.state import State, StatesGroup


class Iskra(StatesGroup):
    select_category = State()
    show_main_report = State()
    send_mail_done = State()
    select_year = State()
    select_month = State()
    show_ks_report = State()
