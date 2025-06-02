import os
from datetime import datetime, timezone

from src.config import Config
from . import db_service

STORAGE_PATH = Config.STORAGE_PATH


def walk_storage_files():
    """
    Рекурсивно сканирует директорию хранилища STORAGE_PATH и собирает метаданные всех файлов.

    Для каждого найденного файла извлекаются:
        - имя файла без расширения,
        - расширение с точкой (например, ".txt"),
        - размер в байтах,
        - относительный путь к директории относительно STORAGE_PATH (пустая строка для корня),
        - время последней модификации файла в UTC.

    Returns:
        list[dict]: Список словарей с информацией о файлах.
            Каждый элемент содержит ключи:
                "name" (str): имя файла без расширения,
                "extension" (str): расширение с точкой,
                "size" (int): размер файла в байтах,
                "path" (str): относительный путь к каталогу,
                "created_at" (datetime): дата и время последней модификации в UTC.
    """
    file_list = []
    for dirpath, _, filenames in os.walk(STORAGE_PATH):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            relative_dir = os.path.relpath(dirpath, STORAGE_PATH)
            if relative_dir in (".", '/', '\\'):
                relative_dir = ""

            stat = os.stat(full_path)
            size = stat.st_size
            created_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

            name, extension = os.path.splitext(filename)
            extension = extension.lstrip(".")

            file_list.append({
                "name": name,
                "extension": f'.{extension}',
                "size": size,
                "path": relative_dir,
                "created_at": created_at,
            })
    return file_list


def sync_files_with_db():
    """
    Синхронизирует содержимое файлового хранилища с записями в базе данных.

    Логика синхронизации:
        - Добавляет в базу данные о новых файлах, найденных в STORAGE_PATH, которых нет в БД.
        - Удаляет из базы записи о файлах, отсутствующих на диске.
    Сопоставление файлов по тройке ключей: имя файла, расширение, относительный путь.

    Returns:
        dict: Результат синхронизации с числом добавленных и удалённых записей:
            {
                "added": int,   # количество добавленных файлов
                "removed": int  # количество удалённых файлов
            }
    """
    storage_files = walk_storage_files()
    db_files = db_service.db_get_all_files()

    # Уникальные ключи
    storage_key_set = {
        (f["name"], f["extension"], f["path"]) for f in storage_files
    }
    db_key_set = {
        (f.name, f.extension, f.path) for f in db_files
    }

    added = 0
    removed = 0

    # Добавляем файлы, которых нет в базе
    for f in storage_files:
        key = (f["name"], f["extension"], f["path"])
        if key not in db_key_set:
            db_service.db_create_file(
                name=f["name"],
                extension=f["extension"],
                size=f["size"],
                path=f["path"],
                created_at=f["created_at"]
            )
            added += 1

    # Удаляем из базы файлы, которых нет в storage
    for file in db_files:
        key = (file.name, file.extension, file.path)
        if key not in storage_key_set:
            db_service.db_delete_file(file.id, silent_if_missing=True)
            removed += 1

    return {
        "added": added,
        "removed": removed
    }
