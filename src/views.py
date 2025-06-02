from flask import Blueprint, request, jsonify, render_template, send_file, abort
from datetime import datetime, UTC
from src.services.file_service import FileService
from src.config import Config

file_routes = Blueprint("file_routes", __name__)
file_service = FileService(Config.STORAGE_PATH)


@file_routes.route('/')
@file_routes.route('/index')
def index():
    return render_template("src/index.html", now=datetime.now(UTC))


@file_routes.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})


@file_routes.route("/files", methods=["GET"])
def list_files():
    files = file_service.get_all_files()
    return jsonify([file.to_dict() for file in files])


@file_routes.route("/files/<int:file_id>", methods=["GET"])
def get_file_detail(file_id: int):
    file = file_service.get_file_detail(file_id)
    return jsonify(file.to_dict())


@file_routes.route("/files/upload", methods=["POST"])
def upload_file():
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

    except Exception as e:
        return jsonify({"message": "Ошибка при загрузке", "error": str(e)}), 500


@file_routes.route("/files/<int:file_id>/update", methods=["PUT"])
def update_file(file_id: int):
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
    try:
        file_service.delete_file(file_id)
        return jsonify({"status": "deleted"})
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Ошибка при удалении файла."}), 500


@file_routes.route("/actualize", methods=["POST"])
def actualize_storage():
    result = file_service.sync_storage_to_db()
    return jsonify(result)


@file_routes.route("/files/<int:file_id>/download", methods=["GET"])
def download_file(file_id):
    file = file_service.get_file_detail(file_id)
    abs_path = file_service.get_file_path(file_id)

    if not abs_path.exists():
        abort(404, description="Файл не найден")

    return send_file(abs_path, as_attachment=True)
