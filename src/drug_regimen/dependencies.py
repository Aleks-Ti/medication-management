from src.drug_regimen.repository import DrugRepository, ManagerRepository, RegimenRepository
from src.drug_regimen.service import DrugService, ManagerService, RegimenService


def drug_service():
    return DrugService(DrugRepository)


def manager_service():
    return ManagerService(ManagerRepository)


def regimen_service():
    return RegimenService(RegimenRepository)
