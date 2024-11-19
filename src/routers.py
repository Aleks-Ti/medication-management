from aiogram.dispatcher.router import Router

from src.drug_regimen.handlers import drug_regimen_router
from src.drug_regimen_manager.handlers import drug_regimen_manager_router
from src.service_handlers import start_router

all_routers: list[Router] = [
    start_router,
    drug_regimen_router,
    drug_regimen_manager_router,
]
