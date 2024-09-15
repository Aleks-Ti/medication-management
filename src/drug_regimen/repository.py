from src.core.postgres_connect import async_session_maker  # noqa
from src.core.repository import SQLAlchemyRepository
from src.drug_regimen.models import Manager, Regimen


class ManagerRepository(SQLAlchemyRepository):
    model: type[Manager] = Manager


class RegimenRepository(SQLAlchemyRepository):
    model: type[Regimen] = Regimen
