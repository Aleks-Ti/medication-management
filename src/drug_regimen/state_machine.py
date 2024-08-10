from aiogram.fsm.state import State, StatesGroup


class ManagerState(StatesGroup):
    """Менеджер-заполнитель данных для курса приема лекарств."""

    name = State()
    start_date = State()
    # month_start_date = State()
    finish_date = State()
    # month_finish_date = State()
    timezone = State()
    cancel = State()


class RegimenState(StatesGroup):
    """Заполнитель режима приема лекарств."""

    hour = State()
    minute = State()
    supplement = State()
    """После еды или до/на тощак/запить/рассосать и тп."""
    add_more = State()
