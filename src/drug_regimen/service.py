from src.core.repository import AbstractRepository
from src.drug_regimen.models import Management
from src.drug_regimen.repository import DrugRegimenRepository


class DrugRegimenService:
    def __init__(self, user_repository: AbstractRepository):
        self.user_repository: DrugRegimenRepository = user_repository()
