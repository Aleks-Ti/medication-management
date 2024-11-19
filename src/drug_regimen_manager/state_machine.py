from aiogram.fsm.state import State, StatesGroup


class UpdateManager(StatesGroup):
    """Менеджер-редактор данных для курса приема лекарств."""

    name = State()
    start_date = State()
    # month_start_date = State()
    finish_date = State()
    # month_finish_date = State()
    timezone = State()


class RegimenState(StatesGroup):
    """Заполнитель режима приема лекарств."""

    hour = State()
    regimen_time = State()
    supplement = State()
    """После еды или до/на тощак/запить/рассосать и тп."""
    add_more = State()
