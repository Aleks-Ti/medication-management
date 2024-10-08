from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from src.drug_regimen.dependencies import manager_service, regimen_service
from src.drug_regimen.state_machine import ManagerState, RegimenState
from src.utils.buttons import MainKeyboard as mk

drug_regimen_router = Router(name="drug_regimen")

TEMP_DATA_FOR_MANAGER = "temp_data_with_date_for_user"


@drug_regimen_router.message(F.text == mk.ADD_DRUG_REGIMEN)
async def manager_start(message: types.Message, state: FSMContext):
    await manager_service().survey_name(message, state)


@drug_regimen_router.message(ManagerState.name)
async def manager_start_date(message: types.Message, state: FSMContext):
    await manager_service().survey_date(message, state)


@drug_regimen_router.callback_query(ManagerState.start_date)
async def manager_survey_finish_date(callback_query: types.CallbackQuery, state: FSMContext):
    await manager_service().survey_finish_date(callback_query, state)


@drug_regimen_router.callback_query(ManagerState.finish_date)
async def manager_timezone(callback_query: types.CallbackQuery, state: FSMContext):
    await manager_service().survey_timezone(callback_query, state)


@drug_regimen_router.callback_query(ManagerState.timezone)
async def regimen_time(callback_query: types.CallbackQuery, state: FSMContext):
    await regimen_service().survey_regimen_time(callback_query, state)


@drug_regimen_router.callback_query(RegimenState.hour)
async def regimen_hour(callback_query: types.CallbackQuery, state: FSMContext):
    await regimen_service().survey_regimen_hour(callback_query, state)


@drug_regimen_router.callback_query(RegimenState.regimen_time)
async def regimen_point_time(callback_query: types.CallbackQuery, state: FSMContext):
    await regimen_service().survey_point_time(callback_query, state)


@drug_regimen_router.message(RegimenState.supplement)
async def regimen_supplement(message: types.Message, state: FSMContext):
    await regimen_service().survey_supplement(message, state)


@drug_regimen_router.callback_query(RegimenState.add_more)
async def regimen_add_more(callback_query: types.CallbackQuery, state: FSMContext):
    await regimen_service().survey_add_more(callback_query, state)
