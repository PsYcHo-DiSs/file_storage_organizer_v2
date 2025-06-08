from datetime import datetime, UTC

from flask import Blueprint, request, jsonify, render_template, send_file, abort
from sqlalchemy.exc import IntegrityError

from src.services.file_service import FileService
from src.config import Config

file_routes = Blueprint("file_routes", __name__)
file_service = FileService(Config.STORAGE_PATH)


@file_routes.route('/')
@file_routes.route('/index')
def index():
    """
    Отображает главную страницу веб-приложения.

    Returns:
        Response: HTML-шаблон главной страницы с текущим временем.
    """
    return render_template("src/index.html", now=datetime.now(UTC))


@file_routes.route("/ping", methods=["GET"])
def ping():
    """
        Проверочный маршрут для проверки доступности сервера.

        Returns:
            JSON: {"status": "ok"}
    """
    return jsonify({"status": "ok"})


@file_routes.route("/files", methods=["GET"])
def list_files():
    """
        Возвращает список всех файлов, зарегистрированных в базе данных.

        Returns:
            JSON: список словарей с информацией о файлах.
    """
    files = file_service.get_all_files()
    return jsonify([file.to_dict() for file in files])


@file_routes.route("/files/<int:file_id>", methods=["GET"])
def get_file_detail(file_id: int):
    """
        Возвращает подробную информацию о конкретном файле по его ID.

        Args:
            file_id (int): идентификатор файла.

        Returns:
            JSON: словарь с информацией о файле.
    """
    file = file_service.get_file_detail(file_id)
    return jsonify(file.to_dict())


@file_routes.route("/files/upload", methods=["POST"])
def upload_file():
    """
        Обрабатывает загрузку нового файла.

        Ожидает multipart/form-data с полями:
        - file (File): сам файл
        - filename (str): желаемое имя файла (с расширением или без)
        - path (str): относительный путь внутри хранилища
        - comment (str, optional): комментарий к файлу

        Returns:
            JSON:
                - 201: данные созданного файла
                - 400: если файл уже существует или введены некорректные данные
                - 500: внутренняя ошибка сервера
        """
    uploaded_file = request.files.get("file")
    name_input = request.form.get("filename", "").strip()
    path = request.form.get("path", "/").strip()
    comment = request.form.get("comment", "").strip()

    if not uploaded_file or not name_input:
        return jsonify({"message": "Имя и файл обязательны"}), 400

    try:
        file = file_service.upload_file(uploaded_file, name_input, path, comment)
        return jsonify(file.to_dict()), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400  # <- пользовательская ошибка
    except IntegrityError:
        return jsonify({"message": "Файл уже существует (на уровне базы)."}), 400

    except Exception as e:
        return jsonify({"message": "Ошибка при загрузке", "error": str(e)}), 500


@file_routes.route("/files/<int:file_id>/update", methods=["PUT"])
def update_file(file_id: int):
    """
        Обновляет имя, путь или комментарий к файлу.

        Ожидает JSON с полями:
        - name (str): новое имя
        - path (str): новый путь
        - comment (str): новый комментарий

        Args:
            file_id (int): Идентификатор файла

        Returns:
            JSON: обновлённая информация о файле или ошибка
        """
    data = request.json
    try:
        updated = file_service.move_file(
            file_id,
            new_name=data.get("name"),
            new_path=data.get("path"),
            new_comment=data.get("comment")
        )
        return jsonify(updated.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@file_routes.route("/files/<int:file_id>/delete", methods=["DELETE"])
def delete_file(file_id: int):
    """
        Удаляет файл и его запись из базы данных.

        Args:
            file_id (int): Идентификатор файла

        Returns:
            JSON:
                - 200: {"status": "deleted"}
                - 404: если файл не найден
                - 500: другая ошибка
        """
    try:
        file_service.delete_file(file_id)
        return jsonify({"status": "deleted"})
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Ошибка при удалении файла."}), 500


@file_routes.route("/actualize", methods=["POST"])
def actualize_storage():
    """
        Синхронизирует файловую систему с базой данных.

        Добавляет недостающие записи о файлах в базе, удаляет записи об отсутствующих файлах.

        Returns:
            JSON: {"added": int, "removed": int}
    """
    result = file_service.sync_storage_to_db()
    return jsonify(result)


@file_routes.route("/files/<int:file_id>/download", methods=["GET"])
def download_file(file_id):
    """
        Отдаёт файл пользователю для скачивания.

        Args:
            file_id (int): Идентификатор файла

        Returns:
            File: потоковое содержимое файла, либо 404 при отсутствии
    """
    file = file_service.get_file_detail(file_id)
    abs_path = file_service.get_file_path(file_id)

    if not abs_path.exists():
        abort(404, description="Файл не найден")

    return send_file(abs_path, as_attachment=True)
