from datetime import datetime

LOCAL_RU_MONTH = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}

INVERSE_LOCAL_RU_MONTH = {value: key for key, value in LOCAL_RU_MONTH.items()}


async def get_user_date(choice_start_data: list[str], user_choice: str) -> datetime:
    count_month = 0
    month_index = 0
    for index, value in enumerate(choice_start_data):
        if INVERSE_LOCAL_RU_MONTH.get(value, False):
            count_month += 1
            if count_month > 1:
                if user_choice in choice_start_data[index:]:
                    month_index = index

    date_now = datetime.now()
    year = date_now.year
    month = INVERSE_LOCAL_RU_MONTH[choice_start_data[month_index]]
    day = user_choice
    result = datetime.strptime(f"{year}.{month}.{day}", "%Y.%m.%d")
    return result
