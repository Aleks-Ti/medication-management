from src.drug_regimen.requests import ManagerApiClient, RegimenApiClient
from src.drug_regimen.service import ManagerService, RegimenService
from src.drug_regimen_manager.dependencies import dr_manager_service
from src.user.dependencies import user_service


def manager_service():
    return ManagerService()


def regimen_service():
    return RegimenService(ManagerApiClient(), RegimenApiClient(), user_service(), dr_manager_service())
