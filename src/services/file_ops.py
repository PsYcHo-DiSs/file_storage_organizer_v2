import os

from src.config import Config
from src.models import FileRecord
from .path_service import sanitize_and_resolve_path, clean_path, sanitize_filename

STORAGE_PATH = Config.STORAGE_PATH


def move_file_if_needed(file: FileRecord, new_name: str, new_user_path: str) -> str:
    """
    Перемещает или переименовывает файл в хранилище при изменении имени или пути.

    Если новое имя файла или путь отличаются от текущих, выполняет перемещение
    (или переименование) файла внутри хранилища. При необходимости создаёт новые каталоги.

    Args:
        file (FileRecord): Объект модели файла с текущими данными (name, extension, path).
        new_name (str): Новое имя файла без расширения.
        new_user_path (str): Новый относительный путь внутри хранилища.

    Returns:
        str: Новый относительный путь (каталог) к файлу после перемещения.

    Raises:
        PermissionError: В случае недостаточных прав для операции с файлом.
        Exception: При возникновении других ошибок во время перемещения.
    """

    old_filename = file.name + file.extension
    new_filename = new_name + file.extension

    old_relative_path = file.path
    new_relative_path = clean_path(new_user_path)

    old_abs_path = os.path.join(STORAGE_PATH, old_relative_path, old_filename)

    if new_relative_path == old_relative_path and new_name == file.name:
        return old_relative_path  # Ничего не изменилось

    try:
        new_abs_path = sanitize_and_resolve_path(STORAGE_PATH, new_relative_path, new_filename)

        os.makedirs(os.path.dirname(new_abs_path), exist_ok=True)

        print(f"==> Пытаюсь переименовать: {old_abs_path} → {new_abs_path}")
        os.rename(old_abs_path, new_abs_path)
        print("==> Переименование прошло успешно.")

    except PermissionError as e:
        print(f"==> Ошибка доступа к файлу: {e}")
        raise e

    except Exception as e:
        print(f"==> Общая ошибка при перемещении файла: {e}")
        raise e

    return new_relative_path


def save_uploaded_file(uploaded_file, name_input: str, user_path: str) -> dict:
    """
    Сохраняет загруженный файл в файловое хранилище и возвращает метаданные.

    Обрабатывает пользовательский ввод имени файла, при необходимости применяет
    очистку имени и пути. Сохраняет файл по итоговому пути.

    Args:
        uploaded_file: объект файла из request.files.
        name_input (str): имя файла, введённое пользователем (может содержать расширение).
        user_path (str): относительный путь в хранилище (например, '/docs').

    Returns:
        dict: Метаданные сохранённого файла с ключами:
            - "name" (str): очищенное имя файла без расширения,
            - "extension" (str): расширение с точкой,
            - "size" (int): размер файла в байтах,
            - "path" (str): относительный путь к каталогу хранения.
    """
    # Получаем оригинальное имя файла БЕЗ secure_filename
    original_filename = uploaded_file.filename.strip()
    original_name, original_ext = os.path.splitext(original_filename)

    # Обработка пользовательского ввода имени
    users_filename, users_file_ext = os.path.splitext(name_input.strip())

    # Если пользователь ничего не ввёл, используем оригинальное имя
    raw_name = users_filename if users_filename else original_name
    name = sanitize_filename(raw_name)

    # Если расширение не указано — берём оригинальное
    extension = users_file_ext if users_file_ext else original_ext

    # Очистка и подготовка пути
    relative_path = clean_path(user_path)

    save_dir = os.path.join(STORAGE_PATH, relative_path)
    os.makedirs(save_dir, exist_ok=True)

    # Сохранение файла
    full_filename = f"{name}{extension}"
    full_path = os.path.join(save_dir, full_filename)
    uploaded_file.save(full_path)
    size = os.path.getsize(full_path)

    return {
        "name": name,
        "extension": extension,
        "size": size,
        "path": relative_path
    }


def delete_physical_file(file: FileRecord, *, silent_if_missing: bool = True) -> bool:
    """
    Удаляет файл из физического хранилища по данным модели.

    Args:
        file (FileRecord): Объект файла с атрибутами name, extension и path.
        silent_if_missing (bool, optional): Если True, отсутствие файла не вызывает ошибку.
                                            Если False, выбрасывается FileNotFoundError.
                                            По умолчанию True.

    Returns:
        bool: True, если файл успешно удалён или отсутствовал при silent_if_missing=True.
              False в остальных случаях.

    Raises:
        FileNotFoundError: если файл не найден и silent_if_missing=False.
        Exception: при возникновении других ошибок при удалении.
    """
    filename = file.name + file.extension
    file_path = os.path.join(STORAGE_PATH, file.path, filename)

    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            print(f"==> Файл удалён: {file_path}")
            return True
        except Exception as e:
            print(f"==> Ошибка при удалении файла: {e}")
            raise e
    else:
        print(f"==> Файл не найден на диске: {file_path}")
        if silent_if_missing:
            return True
        else:
            raise FileNotFoundError(f"Файл {file_path} не найден.")
