from src.drug_regimen.handlers import drug_regimen_router
from src.service_handlers import start_router

all_routers = [
    start_router,
    drug_regimen_router,
]
