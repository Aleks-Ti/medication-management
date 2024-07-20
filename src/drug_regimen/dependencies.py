from src.drug_regimen.repository import DrugRegimenRepository
from src.drug_regimen.service import DrugRegimenService


def drug_regimen_service():
    return DrugRegimenService(DrugRegimenRepository)
