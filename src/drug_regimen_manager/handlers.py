import logging

import httpx
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from src.drug_regimen_manager.dependencies import dr_manager_service
from src.drug_regimen_manager.state_machine import RegimenState, UpdateManager
from src.utils.buttons import MainKeyboard as mk

drug_regimen_manager_router = Router(name="drug_regimen_manager")


@drug_regimen_manager_router.message(F.text == mk.ME_DRUG_REGIMEN)
async def get_all_my(message: types.Message, state: FSMContext):
    try:
        await dr_manager_service().get_all_managers_for_user(message, state)
    except Exception as err:
        logging.exception(f"Error handler manager_start: {err}")
        raise


# @drug_regimen_manager_router.message(ManagerState.name)
# async def manager_start_date(message: types.Message, state: FSMContext):
#     try:
#         await manager_service().survey_date(message, state)
#     except Exception as err:
#         logging.exception(f"Error handler manager_start_date: {err}")
#         raise
