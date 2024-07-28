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


class DrugState(StatesGroup):
    """Сборщик информации о конкретном приёме лекарства."""

    name = State()
    day_start_date = State()
    month_start_date = State()
    day_finish_date = State()
    month_finish_date = State()
    cancel = State()


class RegimenState(StatesGroup):
    """Заполнитель режима приема лекарств."""

    name = State()
    drug_time = State()
    supplement = State()
    """После еды или до/на тощак/запить/рассосать и тп."""
    cancel = State()
