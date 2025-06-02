import os
import re
from dotenv import load_dotenv

load_dotenv()


def str_to_bool(value: str | None) -> bool:
    """
    Конвертирует строку в булево значение.
    Считаются True: 'true', '1', 'yes', 'on' (регистр не важен).
    Иначе False.
    """
    if value is None:
        return False
    return value.lower() in ('true', '1', 'yes', 'on')


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    STORAGE_PATH: str = os.path.join(BASE_DIR, 'storage')
    OS = os.name.lower()
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = str_to_bool(os.getenv('SQLALCHEMY_ECHO'))
    SECRET_KEY = os.getenv('SECRET_KEY')
    WTF_CSRF_ENABLED = str_to_bool(os.getenv('WTF_CSRF_ENABLED'))
    DEBUG = str_to_bool(os.getenv('FLASK_DEBUG'))

    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Нормализует путь в зависимости от ОС:
        - для Windows: все '/' → '\\'
        - для Unix-подобных: все '\\' → '/'
        """
        os_flag = Config.OS
        if 'win' in os_flag or os_flag == 'nt' or os_flag == 'windows_nt':
            # Windows
            return re.sub(r'/', r'\\', path)
        else:
            # Linux / Docker / MacOS
            return re.sub(r'\\', r'/', path)
