from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    """
        Создаёт и настраивает Flask-приложение.

        Инициализирует конфигурацию, подключает базу данных, регистрирует маршруты
        и обеспечивает наличие директории для хранения файлов.

        Returns:
            Flask: экземпляр Flask-приложения с настроенной конфигурацией и зарегистрированными маршрутами.
        """
    app = Flask(__name__)

    from .config import Config
    app.config.from_object(Config)

    # Инициализация БД
    db.init_app(app)

    # Регистрация маршрутов
    from .views import file_routes
    app.register_blueprint(file_routes)

    # Убедимся, что папка хранения файлов существует
    os.makedirs(app.config['STORAGE_PATH'], exist_ok=True)

    return app
