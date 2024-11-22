import logging
import re

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from src.drug_regimen_manager.dependencies import dr_manager_service
from src.drug_regimen_manager.state_machine import UpdateRegimenStiker, UpdateRegimenTime
from src.utils.buttons import MainKeyboard as mk

drug_regimen_manager_router = Router(name="drug_regimen_manager")


@drug_regimen_manager_router.message(F.text == mk.ME_DRUG_REGIMEN)
async def get_all_my(message: types.Message, state: FSMContext) -> None:
    try:
        await state.clear()
        await dr_manager_service().get_all_managers_for_user(message, state)
    except Exception as err:
        logging.exception(f"Error handler manager_start: {err}")
        raise


@drug_regimen_manager_router.callback_query(lambda c: c.data == "settings_manager")
async def settings_manager(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await dr_manager_service().settings_manager(callback_query, state)
    except Exception as err:
        logging.exception(f"Error handler manager_start_date: {err}")
        raise


@drug_regimen_manager_router.callback_query(lambda c: re.match(r"edit_manager_№\d+", c.data))
async def choices_manager(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await dr_manager_service().choice_manager(callback_query, state)
    except Exception as err:
        logging.exception(f"Error handler choices_manager: {err}")
        raise


@drug_regimen_manager_router.callback_query(lambda c: re.match(r"delete_manager_№\d+", c.data))
async def delete_manager(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await dr_manager_service().delete_manager(callback_query, state)
    except Exception as err:
        logging.exception(f"Error handler edit_choice_manager: {err}")
        raise


@drug_regimen_manager_router.callback_query(lambda c: re.match(r"choice_regimens_by_manager_№\d+", c.data))
async def choice_regimens(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await dr_manager_service().choice_regimens(callback_query, state)
    except Exception as err:
        logging.exception(f"Error handler choice_regimens: {err}")
        raise


@drug_regimen_manager_router.callback_query(lambda c: re.match(r"edit_regimen_№\d+", c.data))
async def edit_regimen(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await dr_manager_service().edit_regimen(callback_query, state)
    except Exception as err:
        logging.exception(f"Error handler edit_regimen: {err}")
        raise


@drug_regimen_manager_router.callback_query(lambda c: c.data == "edit_regimen_time")
async def survey_regimen_hour(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await dr_manager_service().survey_regimen_hour(callback_query, state)
    except Exception as err:
        logging.exception(f"Error handler survey_regimen_hour: {err}")
        raise


@drug_regimen_manager_router.callback_query(UpdateRegimenTime.hour)
async def survey_regimen_minute(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await dr_manager_service().survey_regimen_minute(callback_query, state)
    except Exception as err:
        logging.exception(f"Error handler survey_regimen_minute: {err}")
        raise


@drug_regimen_manager_router.callback_query(UpdateRegimenTime.minute)
async def update_regimen_time(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await dr_manager_service().update_regimen_time(callback_query, state)
    except Exception as err:
        logging.exception(f"Error handler update_regimen_time: {err}")
        raise


@drug_regimen_manager_router.callback_query(lambda c: c.data == "edit_regimen_stiker")
async def edit_regimen_stiker(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await dr_manager_service().edit_regimen_stiker(callback_query, state)
    except Exception as err:
        logging.exception(f"Error handler edit_regimen_stiker: {err}")
        raise


@drug_regimen_manager_router.message(UpdateRegimenStiker.value)
async def update_regimen_stiker(message: types.Message, state: FSMContext) -> None:
    try:
        await dr_manager_service().update_regimen_stiker(message, state)
    except Exception as err:
        logging.exception(f"Error handler update_regimen_stiker: {err}")
        raise
