from src.models import FileRecord
from src import db
from datetime import datetime


class FileRepository:
    """
        Репозиторий для доступа к данным файлов в базе данных. Предоставляет CRUD-операции
        и проверку существования записей.
    """
    @staticmethod
    def exists(name: str, extension: str, path: str) -> bool:
        """
            Проверяет наличие записи в БД по имени, расширению и пути.

            Returns:
                bool: True, если такая запись есть.
        """
        return FileRecord.query.filter_by(name=name, extension=extension, path=path).first() is not None

    @staticmethod
    def get_by_id(file_id: int) -> FileRecord:
        """
            Получает объект файла по ID, или выбрасывает 404.

            Returns:
                FileRecord: Объект из базы.
        """
        return FileRecord.query.get_or_404(file_id)

    @staticmethod
    def get_all() -> list[FileRecord]:
        """
            Возвращает все записи файлов.

            Returns:
                list[FileRecord]: Список всех объектов FileRecord.
        """
        return FileRecord.query.all()

    @staticmethod
    def create(name: str, extension: str, size: int, path: str, created_at: datetime,
               comment: str = None) -> FileRecord:
        """
            Создаёт новую запись о файле в базе данных.

            Returns:
                FileRecord: Созданный объект.
        """
        file = FileRecord(name=name, extension=extension, size=size, path=path, created_at=created_at, comment=comment)
        db.session.add(file)
        db.session.commit()
        return file

    @staticmethod
    def delete(file: FileRecord):
        """
            Удаляет запись из базы.

            Args:
                file (FileRecord): Объект для удаления.
        """
        db.session.delete(file)
        db.session.commit()

    @staticmethod
    def update(file: FileRecord, **fields):
        """
            Обновляет поля записи о файле.

            Args:
                file (FileRecord): Запись в БД.
                **fields: Произвольные поля (name, path, comment и т.д.).

            Returns:
                FileRecord: Обновлённая запись.
        """
        for attr, value in fields.items():
            setattr(file, attr, value)
        file.updated_at = datetime.now()
        db.session.commit()
        return file
