from src.drug_regimen.repository import ManagerRepository, RegimenRepository
from src.drug_regimen.service import ManagerService, RegimenService
from src.user.repository import UserRepository


def manager_service():
    return ManagerService(ManagerRepository, UserRepository)


def regimen_service():
    return RegimenService(RegimenRepository, UserRepository)
