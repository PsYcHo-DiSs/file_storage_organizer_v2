from datetime import datetime, UTC

from src.config import Config
from src.models import FileRecord
from src import db
from .file_ops import move_file_if_needed, save_uploaded_file, delete_physical_file

STORAGE_PATH = Config.STORAGE_PATH


def db_get_all_files():
    """
    Получает все записи файлов из базы данных.

    Returns:
        list[FileRecord]: список всех объектов FileRecord.
    """
    return FileRecord.query.all()


def db_get_file_by_id(file_id: int):
    """
    Получает запись файла по ID.

    Args:
        file_id (int): ID записи.

    Returns:
        FileRecord: объект записи файла.

    Raises:
        sqlalchemy.orm.exc.NoResultFound: если запись не найдена.
    """
    return FileRecord.query.get_or_404(file_id)


def db_create_file(name: str, extension: str, size: int, path: str, created_at=datetime.now(UTC), comment=None):
    """
    Создаёт новую запись файла в базе данных.

    Args:
        name (str): Имя файла без расширения.
        extension (str): Расширение файла с точкой (например, ".txt").
        size (int): Размер файла в байтах.
        path (str): Относительный путь к файлу в файловом хранилище.
        created_at (datetime, optional): Время создания файла. По умолчанию текущее UTC время.
        comment (str, optional): Комментарий к файлу.

    Returns:
        FileRecord: Созданный объект записи файла.
    """
    file = FileRecord(
        name=name,
        extension=extension,
        size=size,
        path=path,
        created_at=created_at,
        comment=comment
    )
    db.session.add(file)
    db.session.commit()
    return file


def db_update_file(file: FileRecord, data: dict) -> None:
    """
    Обновляет запись файла в базе и перемещает физический файл при изменении имени или пути.

    При изменении имени или пути файла, файл на диске будет перемещён в новое место.
    Также обновляется комментарий и время последнего обновления записи.

    Args:
        file (FileRecord): Существующая запись файла для обновления.
        data (dict): Словарь с новыми значениями полей. Поддерживаемые ключи:
            - 'name' (str): Новое имя файла без расширения.
            - 'path' (str): Новый относительный путь к файлу.
            - 'comment' (str): Новый комментарий к файлу.

    Returns:
        None
    """

    new_name = data.get('name', file.name)
    new_user_path = data.get('path', file.path)
    if new_user_path in ("", "/", ".", "\\", None):
        new_user_path = ""  # нормализуем в пустую строку — означает корень

    new_comment = data.get('comment', file.comment)

    new_relative_path = move_file_if_needed(file, new_name, new_user_path)

    # Обновим поля
    file.name = new_name
    file.path = new_relative_path
    file.comment = new_comment
    file.updated_at = datetime.now(UTC)

    db.session.commit()


def db_delete_file(file_id: int, *, silent_if_missing: bool = True) -> None:
    """
    Удаляет запись о файле из базы данных и сам файл из хранилища.
    Если физический файл отсутствует и silent_if_missing=True,
    исключение не выбрасывается, что удобно для синхронизации.

    Args:
        file_id (int): ID файла.
        silent_if_missing (bool): если True — отсутствие файла на диске не вызывает ошибку (для sync).
    Returns:
        None
    """
    file = db_get_file_by_id(file_id)

    # Удаляем физический файл (если есть)
    delete_physical_file(file, silent_if_missing=silent_if_missing)

    db.session.delete(file)
    db.session.commit()
    print(f"==> Удалена запись из БД: {file.name}{file.extension}")


def db_create_file_from_upload(uploaded_file, name_input: str, path: str, comment: str = "") -> FileRecord:
    """
    Обрабатывает загруженный файл: сохраняет на диск и создаёт запись в базе.

    Args:
        uploaded_file (werkzeug.datastructures.FileStorage): Загруженный файл из формы.
        name_input (str): Имя файла, введённое пользователем (без расширения).
        path (str): Относительный путь в файловом хранилище, куда сохранить файл.
        comment (str, optional): Комментарий к файлу. По умолчанию пустая строка.

    Returns:
        FileRecord: Созданная запись файла в базе.
    """
    meta = save_uploaded_file(uploaded_file, name_input, path)
    new_file = db_create_file(**meta, comment=comment)
    db.session.add(new_file)
    db.session.commit()
    return new_file
