import re


def validate_input(text: str) -> bool:
    """
    Проверяет текст на наличие запрещённых символов или конструкций.
    Возвращает True, если текст безопасен, иначе False.
    """
    # Запрещённые символы или последовательности
    forbidden_patterns = [
        r"[<>]",  # Угловые скобки
        r"['\"`]",  # Одинарные/двойные кавычки и бэктики
        r"(?:--|;|/\*|\*/)",  # SQL-инъекции
        r"(?:<script>|</script>)",  # JavaScript-инъекции
        r"\b(?:DROP|SELECT|INSERT|DELETE|UPDATE|CREATE|ALTER)\b",  # SQL команды
    ]
    # Проверяем длину текста
    if len(text) > 128:  # Лимит длины текста
        return False

    for pattern in forbidden_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False

    return True
