import os
import re
from unidecode import unidecode

from src.config import Config
from src.models import FileRecord


def sanitize_filename(name: str) -> str:
    """
    Преобразует имя файла в безопасный формат.

    Выполняет транслитерацию кириллицы в латиницу, заменяет все символы,
    кроме латинских букв, цифр, подчёркиваний, дефисов и точек, на подчёркивания,
    а также удаляет ведущие и конечные подчёркивания.

    Args:
        name (str): Исходное имя файла.

    Returns:
        str: Очищенное и транслитерированное имя файла, безопасное для использования.
    """
    name = unidecode(name)  # Транслитерация кириллицы
    name = re.sub(r'[^A-Za-z0-9_\-\.]+', '_', name)  # Только латиница, цифры, _, -, .
    return name.strip('_')


def sanitize_path_components(path: str) -> str:
    """
    Транслитерирует и очищает каждую часть пути, сохраняя структуру директорий.

    Разбивает путь по разделителям '/', '\\', очищает каждую часть с помощью
    sanitize_filename и соединяет обратно с системным разделителем.

    Args:
        path (str): Исходный путь, возможно содержащий небезопасные символы и кириллицу.

    Returns:
        str: Безопасный путь с транслитерированными и очищенными компонентами.
    """
    normalized = Config.normalize_path(path.strip())

    parts = re.split(r'[\\/]', normalized)  # разбиваем по / или \
    sanitized_parts = [sanitize_filename(part) for part in parts if part]

    sep = '\\' if 'win' in Config.OS else '/'
    return sep.join(sanitized_parts)


def clean_path(path: str) -> str:
    """
    Заглушка для очистки пользовательского пути.

    В текущей реализации функция выполняет транслитерацию и очистку компонентов пути
    без изменения структуры, чтобы не нарушать организацию папок.

    Args:
        path (str): Исходный пользовательский путь.

    Returns:
        str: Очищенный путь с безопасными именами директорий.
    """

    return sanitize_path_components(path)


def sanitize_and_resolve_path(base_dir: str, user_path: str, filename: str) -> str:
    """
    Формирует безопасный абсолютный путь к файлу, предотвращая выход за пределы базовой директории.

    Очищает и транслитерирует пользовательский путь и имя файла,
    затем объединяет их с базовой директорией, и проверяет, что итоговый путь
    находится внутри базовой директории.

    Args:
        base_dir (str): Абсолютный путь к базовой директории хранения файлов.
        user_path (str): Пользовательский относительный путь к файлу.
        filename (str): Имя файла (может содержать расширение).

    Returns:
        str: Абсолютный безопасный путь к файлу.

    Raises:
        ValueError: Если итоговый путь выходит за пределы базовой директории.
    """
    filename = os.path.basename(filename)  # защита от ../file.txt
    cleaned_path = clean_path(user_path)   # теперь включает транслит папок
    cleaned_filename = sanitize_filename(filename)

    full_path = os.path.abspath(os.path.join(base_dir, cleaned_path, cleaned_filename))

    if not full_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Недопустимый путь: выход за пределы базовой директории")

    return full_path


def get_file_absolute_path(file: FileRecord) -> str:
    """
    Возвращает абсолютный путь к файлу в хранилище на основе данных модели.

    Args:
        file (FileRecord): Объект модели файла.

    Returns:
        str: Абсолютный путь к файлу в файловой системе.
    """
    filename = file.name + file.extension
    return os.path.join(Config.STORAGE_PATH, file.path, filename)
