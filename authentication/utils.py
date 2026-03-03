import os
import resend
import secrets
from dotenv import load_dotenv
from resend.exceptions import ResendError


# Загружаем переменные окружения из файла .env
load_dotenv()


def generate_strong_6_digit_number():
    """Генерирует криптографически стойкое случайное 6-значное число в виде строки."""

    # secrets.randbelow(1_000_000) генерирует случайное число от 0 до 999999
    random_int = secrets.randbelow(1_000_000)

    # Форматируем число с ведущими нулями до 6 знаков и преобразуем в int
    return int(f"{random_int:06d}")


def send_verification_email(code: str, email: str) -> bool:
    """
    Отправляет код подтверждения на email пользователя
    
    Аргументы:
        code: код подтверждения для отправки
        email: email получателя
    
    Возвращает:
        True если отправка успешна, False в противном случае
    """

    try:
        # Устанавливаем API ключ для сервиса Resend
        resend.api_key = os.getenv("RESEND_API_KEY")

        # Получаем данные отправителя из переменных окружения
        from_name = os.getenv("FROM_NAME")
        from_email = os.getenv("FROM_EMAIL")

        # Формируем параметры для отправки email
        params: resend.Emails.SendParams = {
            "from": f"{from_name} <{from_email}>",  # Отправитель в формате "Имя <email>"
            "to": [f"{email}"],                      # Получатель
            "subject": "Verification Code",           # Тема письма
            "html": f"Here is the verification code you requested: {code}",  # HTML-содержимое
        }

        # Отправляем email через сервис Resend
        email = resend.Emails.send(params)

        return True

    except ResendError:
        # В случае ошибки отправки возвращаем False
        return False