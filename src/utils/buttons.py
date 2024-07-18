from aiogram import types


class MainKeyboard:
    """
    Кнопки для главного меню.

    Attributes:
    - ADD_DRUG_REGIMEN = 'Добавить план/схему приёма лекарств'
    - ME_DRUG_REGIMEN = 'Мои группы приёма лекарств'
    - cancel = 'Отмена'
    """

    ADD_DRUG_REGIMEN: str = "Добавить план/схему приёма лекарств"
    ME_DRUG_REGIMEN: str = "Мои группы приёма лекарств"
    cancel: str = "Отмена"


async def inline_buttons_generator(buttons: list[str, int], prefix=None, postfix=None) -> list:
    max_button_one_page = 3
    result_list_buttons = []
    temp_list_buttons = []
    count = 0
    for value in buttons:
        text = f"{prefix if prefix else ''}{value if isinstance(value, str) else str(value)}{postfix if postfix else ''}"
        if count == max_button_one_page:
            result_list_buttons.append(temp_list_buttons)
            temp_list_buttons = []
            count = 0  # because clear temp_list_buttons
            temp_list_buttons.append(types.InlineKeyboardButton(text=text, callback_data=text))
            count += 1  # + 1 because after clearing the list, a subsequent button from the iteration has already been added
        else:
            temp_list_buttons.append(types.InlineKeyboardButton(text=text, callback_data=text))
            count += 1
    if temp_list_buttons is not None:
        result_list_buttons.append(temp_list_buttons)
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=result_list_buttons,
    )
    return keyboard
