from src.core.repository import AbstractRepository
from src.drug_regimen.models import Drug, Manager, Regimen
from src.drug_regimen.repository import DrugRepository, ManagerRepository, RegimenRepository


class DrugService:
    def __init__(self, drug_repository: AbstractRepository):
        self.drug_repository: DrugRepository = drug_repository()


class RegimenService:
    def __init__(self, regimen_repository: AbstractRepository):
        self.regimen_repository: RegimenRepository = regimen_repository()


class ManagerService:
    def __init__(self, manager_repository: AbstractRepository):
        self.manager_repository: ManagerRepository = manager_repository()
