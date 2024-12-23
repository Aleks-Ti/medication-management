from aiogram import types


class MainKeyboard:
    """
    Кнопки для главного меню.

    Attributes:
    - ADD_DRUG_REGIMEN = 'Добавить план/схему приёма лекарств'
    - ME_DRUG_REGIMEN = 'Мои группы приёма лекарств'
    - cancel = 'Отмена'
    """

    ADD_DRUG_REGIMEN: str = "Добавить курс/схему напоминаний"
    ME_DRUG_REGIMEN: str = "Мои курсы и напоминания"
    CANCEL: str = "Отмена действия"


class BaseMenuKeyboard:
    """
    Кнопки для всплывающего меню.

    Attributes:
    - START = "/start" -> START_DESCRIPTION = "Старт/Перезапуск"
    - HELP = "/help" -> HELP_DESCRIPTION = "Справка"
    - CANCEL = "/cancel" -> CANCEL_DESCRIPTION = "Отмена"
    """

    START: str = "start"
    HELP: str = "help"
    CANCEL: str = "cancel"

    START_DESCRIPTION: str = "Старт/Перезапуск"
    HELP_DESCRIPTION: str = "Справка"
    CANCEL_DESCRIPTION: str = "Отмена действия"


BOT_MENU_COMMANDS = [
    types.BotCommand(command=BaseMenuKeyboard.START, description=BaseMenuKeyboard.START_DESCRIPTION),
    types.BotCommand(command=BaseMenuKeyboard.HELP, description=BaseMenuKeyboard.HELP),
    types.BotCommand(command=BaseMenuKeyboard.CANCEL, description=BaseMenuKeyboard.CANCEL_DESCRIPTION),
]


class InlineButtonsGenerator:
    @staticmethod
    async def inline_buttons_generator(
        buttons: list[str | int] | range,
        prefix=None,
        postfix=None,
        callback_unique_indetifier=None,
        prefix_mask=None,
    ) -> types.InlineKeyboardMarkup:
        max_button_one_page = 3
        result_list_buttons: list = []
        temp_list_buttons: list = []
        count = 0
        for value in buttons:
            text = f"{prefix if prefix else ''}{value if isinstance(value, str) else str(value)}{postfix if postfix else ''}"
            if count == max_button_one_page:
                result_list_buttons.append(temp_list_buttons)
                temp_list_buttons = []
                count = 0  # because clear temp_list_buttons
                temp_list_buttons.append(
                    types.InlineKeyboardButton(
                        text=text if not prefix_mask else prefix_mask + text,
                        callback_data=callback_unique_indetifier + text if callback_unique_indetifier else text,
                    ),
                )
                count += 1  # + 1 because after clearing the list, a subsequent button from the iteration has already been added
            else:
                temp_list_buttons.append(
                    types.InlineKeyboardButton(
                        text=text if not prefix_mask else prefix_mask + text,
                        callback_data=callback_unique_indetifier + text if callback_unique_indetifier else text,
                    ),
                )
                count += 1
        if temp_list_buttons is not None:
            result_list_buttons.append(temp_list_buttons)
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=result_list_buttons,
        )
        return keyboard

    @staticmethod
    async def get_string_representation_pool_inline_buttons(keyboard: types.InlineKeyboardMarkup) -> list[str]:
        temp: list[str] = [x[0].text if len(x) == 1 else ",".join([x.text for x in x]) for x in keyboard.inline_keyboard]
        result = []
        for x in temp:
            if x.isdigit():
                result.append(x)
            else:
                if x[0].isdigit():
                    for j in x.split(","):
                        result.append(j)
                else:
                    result.append(x)
        return result

    @staticmethod
    async def yes_or_not_inline_buttons() -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Да", callback_data="yes")],
                [types.InlineKeyboardButton(text="Нет", callback_data="no")],
            ],
        )
        return keyboard

    @staticmethod
    async def delete_manager_or_regimen_edit_inline_buttons(
        exlude_regimen_button: bool,
        postfix: str,
    ) -> types.InlineKeyboardMarkup:
        if exlude_regimen_button:
            keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="Удалить курс №" + postfix,
                            callback_data="delete_manager_№" + postfix,
                        ),
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="Редактировать напоминания",
                            callback_data="choice_regimens_by_manager_№" + postfix,
                        ),
                    ],
                ],
            )
        else:
            keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="Удалить курс №" + postfix, callback_data="delete_manager_№" + postfix)],
                ],
            )
        return keyboard

    @staticmethod
    async def manager_inline_button() -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Редактировать курсы", callback_data="settings_manager")],
            ],
        )
        return keyboard

    @staticmethod
    async def edit_regimen_values_inline_button() -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Редактировать Время", callback_data="edit_regimen_time")],
                [types.InlineKeyboardButton(text="Редактировать Стикер", callback_data="edit_regimen_stiker")],
            ],
        )
        return keyboard
