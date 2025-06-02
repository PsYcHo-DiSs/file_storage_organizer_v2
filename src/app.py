import os
from src import create_app, db
from dotenv import load_dotenv
from src.config import Config

load_dotenv()

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    """
        Точка входа в приложение.

        Инициализирует Flask-приложение, создаёт все таблицы в базе данных
        при первом запуске и запускает сервер в режиме отладки.
    """
    app.run(host='0.0.0.0', debug=Config.DEBUG)
