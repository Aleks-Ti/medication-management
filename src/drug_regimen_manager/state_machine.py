from aiogram.fsm.state import State, StatesGroup


class UpdateRegimenStiker(StatesGroup):
    value = State()


class UpdateRegimenTime(StatesGroup):
    hour = State()
    minute = State()
