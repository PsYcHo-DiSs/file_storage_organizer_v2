from datetime import datetime, UTC
from . import db


class FileRecord(db.Model):
    """
        Модель файла в системе хранения.

        Атрибуты:
            id (int): Уникальный идентификатор файла.
            name (str): Имя файла без расширения.
            extension (str): Расширение файла (включая точку).
            size (int): Размер файла в байтах.
            path (str): Относительный путь к директории, в которой находится файл.
            created_at (datetime): Дата создания файла.
            updated_at (datetime | None): Дата последнего изменения информации о файле.
            comment (str | None): Пользовательский комментарий к файлу.
        """
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    extension = db.Column(db.String(20), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=lambda: datetime.now(UTC), nullable=True)
    comment = db.Column(db.String(1024), nullable=True)

    def to_dict(self):
        """
                Конвертирует объект записи файла в словарь для JSON-сериализации.

                Returns:
                    dict: словарь с ключами id, name, extension, size, path, created_at, updated_at, comment.
                """
        return {
            "id": self.id,
            "name": self.name,
            "extension": self.extension,
            "size": self.size,
            "path": self.path,
            "created_at": self.created_at,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "comment": self.comment,
        }
