from src.models import FileRecord
from src import db
from datetime import datetime


class FileRepository:
    @staticmethod
    def exists(name: str, extension: str, path: str) -> bool:
        return FileRecord.query.filter_by(name=name, extension=extension, path=path).first() is not None

    @staticmethod
    def get_by_id(file_id: int) -> FileRecord:
        return FileRecord.query.get_or_404(file_id)

    @staticmethod
    def get_all() -> list[FileRecord]:
        return FileRecord.query.all()

    @staticmethod
    def create(name: str, extension: str, size: int, path: str, created_at: datetime,
               comment: str = None) -> FileRecord:
        file = FileRecord(name=name, extension=extension, size=size, path=path, created_at=created_at, comment=comment)
        db.session.add(file)
        db.session.commit()
        return file

    @staticmethod
    def delete(file: FileRecord):
        db.session.delete(file)
        db.session.commit()

    @staticmethod
    def update(file: FileRecord, **fields):
        for attr, value in fields.items():
            setattr(file, attr, value)
        file.updated_at = datetime.now()
        db.session.commit()
        return file
