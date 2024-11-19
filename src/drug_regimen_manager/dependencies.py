from src.drug_regimen.requests import ManagerApiClient, RegimenApiClient
from src.drug_regimen_manager.service import DrManagerService
from src.user.dependencies import user_service
from src.user.requests import UserApiClient


def dr_manager_service() -> DrManagerService:
    return DrManagerService(ManagerApiClient(), RegimenApiClient(), UserApiClient())
