import os
from flask import Blueprint, jsonify, request, render_template, send_from_directory, abort

from src.services.db_service import *
from services.sync_service import sync_files_with_db
from src.services.path_service import get_file_absolute_path

file_routes = Blueprint("file_routes", __name__)


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
    files = db_get_all_files()
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
    file = db_get_file_by_id(file_id)
    return jsonify(file.to_dict())


@file_routes.route("/files/upload", methods=["POST"])
def upload_file():
    """
    Обрабатывает загрузку нового файла в файловое хранилище.

    Ожидает multipart/form-data с параметрами:
    - file: сам файл
    - filename: желаемое имя файла (без расширения)
    - path: относительный путь в хранилище
    - comment: комментарий к файлу (опционально)

    Returns:
        JSON: результат загрузки (успех или ошибка с сообщением).
    """
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return jsonify({"message": "Файл не прикреплён"}), 400

    name_input = request.form.get("filename", "").strip()
    path = request.form.get("path", "/").strip()
    comment = request.form.get("comment", "").strip()

    if not name_input or not path:
        return jsonify({"message": "Имя и путь обязательны"}), 400

    try:
        db_create_file_from_upload(uploaded_file, name_input, path, comment)
        return jsonify({"message": "Файл загружен успешно"})
    except Exception as e:
        return jsonify({"message": "Ошибка при загрузке", "error": str(e)}), 500


@file_routes.route("/files/<int:file_id>/update", methods=["PUT"])
def update_file(file_id: int):
    """
    Обновляет информацию о файле по его ID.

    Ожидает JSON с возможными новыми значениями:
    - name (str): новое имя файла (без расширения)
    - path (str): новый относительный путь к файлу
    - comment (str): обновлённый комментарий

    Производит перемещение файла на диске, если имя или путь изменились,
    и обновляет соответствующую запись в базе данных.

    Args:
        file_id (int): ID файла в базе данных

    Returns:
        JSON: результат операции с полем "success" и, при ошибке, сообщением об ошибке.
    """
    file = db_get_file_by_id(file_id)
    data = request.json
    try:
        db_update_file(file, data)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@file_routes.route("/files/<int:file_id>/delete", methods=["DELETE"])
def delete_file(file_id: int):
    """
    Удаляет запись о файле из базы данных и сам файл из хранилища.

    Args:
        file_id (int): идентификатор файла.

    Returns:
        JSON: статус удаления или сообщение об ошибке.
    """
    try:
        db_delete_file(file_id, silent_if_missing=False)
        return jsonify({"status": "deleted"})
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Ошибка при удалении файла."}), 500


@file_routes.route("/actualize", methods=["POST"])
def actualize_storage():
    """
        Синхронизирует содержимое хранилища с базой данных,
        добавляя новые файлы и удаляя отсутствующие.

        Returns:
            JSON: количество добавленных и удалённых записей.
        """
    result = sync_files_with_db()
    return jsonify({
        "status": "ok",
        "added": result["added"],
        "removed": result["removed"]
    })


@file_routes.route("/files/<int:file_id>/download", methods=["GET"])
def download_file(file_id):
    """
        Предоставляет файл для скачивания по ID.

        Args:
            file_id (int): идентификатор файла.

        Returns:
            Response: потоковый ответ с файлом или 404, если файл не найден.
        """
    file = db_get_file_by_id(file_id)
    filename = file.name + file.extension
    abs_path = get_file_absolute_path(file)

    if not os.path.exists(abs_path):
        abort(404, description="Файл не найден")

    # Разделяем директорию и имя файла
    directory = os.path.dirname(abs_path)
    return send_from_directory(directory, filename, as_attachment=True)
