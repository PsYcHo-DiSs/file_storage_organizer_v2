from datetime import datetime, UTC
from pathlib import Path
from src.services.storage_manager import StorageManager
from src.services.file_repository import FileRepository
from src.models import FileRecord


class FileService:
    """
        Сервисный слой, объединяющий файловую систему и базу данных.
        Отвечает за обработку файлов: загрузку, перемещение, удаление и синхронизацию.
    """
    def __init__(self, storage_dir: str):
        self.storage = StorageManager(storage_dir)  # Файловая система
        self.repo = FileRepository()  # Общается с базой

    def upload_file(self, file_storage, name_input: str, path: str, comment: str = "") -> FileRecord:
        """
            Загружает файл: сохраняет в хранилище и создаёт запись в БД.
            Предотвращает дублирование файлов.

            Returns:
                FileRecord: Сохранённый файл.
            Raises:
                ValueError: Если файл с таким именем уже существует в указанной директории.
        """
        meta = self.storage.save_uploaded_file(file_storage, name_input, path)
        if self.repo.exists(meta["name"], meta["extension"], meta["path"]):
            raise ValueError("Файл с таким именем уже существует по данному пути.")
        return self.repo.create(**meta, created_at=datetime.now(UTC), comment=comment)

    def move_file(self, file_id: int, new_name: str, new_path: str, new_comment: str = None):
        """
            Перемещает и переименовывает файл, обновляя запись в базе.

            Returns:
                FileRecord: Обновлённая запись.
        """
        file = self.repo.get_by_id(file_id)
        new_rel_path = self.storage.move_file(file, new_name, new_path)
        return self.repo.update(file, name=new_name, path=new_rel_path, comment=new_comment or file.comment)

    def delete_file(self, file_id: int):
        """
            Удаляет файл и его запись из базы.

            Args:
                file_id (int): Идентификатор файла.
        """
        file = self.repo.get_by_id(file_id)
        self.storage.delete_file(file)
        self.repo.delete(file)

    def sync_storage_to_db(self) -> dict:
        """
            Сравнивает хранилище с базой данных:
            - добавляет записи о новых файлах;
            - удаляет записи об отсутствующих на диске.

            Returns:
                dict: {"added": int, "removed": int}
        """
        # Файлы, записи о которых есть в базе
        db_files = self.repo.get_all()
        # Список словарей, с инфой о файлах, которые физически находятся в файловом хранилище
        storage_files = self.storage.scan_storage()

        db_key_set = {
            (f.name, f.extension, f.path) for f in db_files
        }
        storage_key_set = {
            (f["name"], f["extension"], f["path"]) for f in storage_files
        }

        added = 0
        removed = 0
        for f in storage_files:
            key = (f['name'], f['extension'], f['path'])
            if key not in db_key_set:
                self.repo.create(
                    name=f['name'],
                    extension=f['extension'],
                    size=f['size'],
                    path=f['path'],
                    created_at=f['created_at']
                )
                added += 1
        for f in db_files:
            key = (f.name, f.extension, f.path)
            if key not in storage_key_set:
                self.repo.delete(f)
                removed += 1

        return {"added": added, "removed": removed}

    def get_all_files(self):
        """
        Получает список всех файлов из БД.

        Returns:
            list[FileRecord]
        """
        return self.repo.get_all()

    def get_file_detail(self, file_id: int):
        """
        Получает подробности файла по ID.

        Returns:
            FileRecord
        """
        return self.repo.get_by_id(file_id)

    def get_file_path(self, file_id: int) -> Path:
        """
            Возвращает абсолютный путь к файлу в хранилище.

            Returns:
                Path: Путь до файла.
        """
        file = self.repo.get_by_id(file_id)
        return Path(self.storage.base_dir) / file.path / (file.name + file.extension)
