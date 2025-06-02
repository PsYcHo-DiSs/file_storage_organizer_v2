from pathlib import Path
import os
from datetime import datetime, timezone
from src.services.path_service import sanitize_and_resolve_path, clean_path, sanitize_filename
from src.models import FileRecord


class StorageManager:
    """
        Отвечает за операции с файловым хранилищем: сохранение, перемещение, удаление файлов
        и сканирование директории хранения.

        Атрибуты:
            base_dir (Path): Абсолютный путь к корневой директории хранилища.
        """

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir).resolve()
        os.makedirs(self.base_dir, exist_ok=True)

    def save_uploaded_file(self, uploaded_file, name_input: str, user_path: str) -> dict:
        """
            Сохраняет загруженный файл в файловое хранилище и возвращает метаданные.

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
        original_filename = uploaded_file.filename.strip()
        original_name, original_ext = os.path.splitext(original_filename)
        users_filename, users_file_ext = os.path.splitext(name_input.strip())
        raw_name = users_filename or original_name
        name = sanitize_filename(raw_name)
        extension = users_file_ext or original_ext
        relative_path = clean_path(user_path)
        save_dir = self.base_dir / relative_path
        save_dir.mkdir(parents=True, exist_ok=True)
        full_filename = f"{name}{extension}"
        full_path = save_dir / full_filename
        uploaded_file.save(str(full_path))
        size = os.path.getsize(full_path)
        return {
            "name": name,
            "extension": extension,
            "size": size,
            "path": relative_path
        }

    def move_file(self, file: FileRecord, new_name: str, new_user_path: str) -> str:
        """
            Перемещает файл на новое место, включая переименование.

            Args:
                file (FileRecord): Запись файла из базы.
                new_name (str): Новое имя файла без расширения.
                new_user_path (str): Новый относительный путь внутри хранилища.

            Returns:
                str: Новый относительный путь к файлу.
            """
        old_filename = file.name + file.extension
        new_filename = new_name + file.extension
        old_relative_path = file.path
        new_relative_path = clean_path(new_user_path)
        old_abs_path = self.base_dir / old_relative_path / old_filename
        if new_relative_path == old_relative_path and new_name == file.name:
            return old_relative_path
        new_abs_path = Path(sanitize_and_resolve_path(str(self.base_dir), new_relative_path, new_filename))
        new_abs_path.parent.mkdir(parents=True, exist_ok=True)
        os.rename(old_abs_path, new_abs_path)
        return new_relative_path

    def delete_file(self, file: FileRecord, *, silent_if_missing: bool = True) -> bool:
        """
            Удаляет физический файл с диска.

                Args:
                    file (FileRecord): Объект файла.
                    silent_if_missing (bool): Не выбрасывать исключение, если файл не найден.

                Returns:
                    bool: True если файл удалён или отсутствует, иначе False.
        """
        filename = file.name + file.extension
        file_path = self.base_dir / file.path / filename
        if file_path.is_file():
            try:
                file_path.unlink()
                return True
            except Exception as e:
                raise e
        elif silent_if_missing:
            return True
        else:
            raise FileNotFoundError(f"Файл {file_path} не найден.")

    def scan_storage(self) -> list[dict]:
        """
            Сканирует файловую систему и возвращает список метаданных всех файлов в хранилище.

            Returns:
                list[dict]: Каждый словарь содержит name, extension, size, path, created_at.
        """
        file_list = []
        for dirpath, _, filenames in os.walk(self.base_dir):
            for filename in filenames:
                full_path = Path(dirpath) / filename
                relative_dir = full_path.parent.relative_to(self.base_dir)
                if str(relative_dir) in (".", '/', '\\'):
                    relative_dir = ""
                stat = full_path.stat()
                size = stat.st_size
                created_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                name, extension = os.path.splitext(filename)
                file_list.append({
                    "name": name,
                    "extension": extension,
                    "size": size,
                    "path": str(relative_dir),
                    "created_at": created_at,
                })
        return file_list
