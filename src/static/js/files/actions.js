import {
fetchFiles,
fetchFileDetail,
updateFile,
deleteFile as apiDeleteFile,
actualizeFiles,
uploadFile
} from "./api.js";

import { renderTable } from "./render.js";

/**
* let currentFileId = null;
*/
window.currentFileId = null;

/**
 * Открывает модальное окно с деталями файла.
 * @param {number} fileId - ID файла
 * @returns {Promise<void>}
 */
export async function openFileDetails(fileId) {
    try {
        const file = await fetchFileDetail(fileId);
        window.currentFileId = fileId;

        document.getElementById("detail-name").value = file.name;
        document.getElementById("detail-extension").textContent = file.extension;
        document.getElementById("detail-size").textContent = file.size;
        document.getElementById("detail-path").placeholder = file.path;
        document.getElementById("detail-created").textContent = file.created_at;
        document.getElementById("detail-updated").textContent = file.updated_at;
        document.getElementById("detail-comment").value = file.comment || "";

        const modal = new bootstrap.Modal(document.getElementById("fileDetailModal"));
        modal.show();
    } catch (error) {
        console.error("Ошибка при загрузке деталей файла:", error);
        alert("Не удалось загрузить информацию о файле.");
    }
}

/**
 * Удаляет файл с подтверждением.
 * @param {number} fileId - ID файла
 * @returns {Promise<void>}
 */
export async function deleteFile(fileId) {
    if (!confirm("Удалить файл?")) return;

    try {
        await apiDeleteFile(fileId);
        const files = await fetchFiles();
        renderTable(files, handlers);

        // Закрываем модальное окно, если оно открыто
        const modalElement = document.getElementById("fileDetailModal");
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
            modalInstance.hide();
        }

    } catch (error) {
        console.error("Ошибка при удалении файла:", error);
        alert("Не удалось удалить файл.");
    }
}

/**
 * Сохраняет изменения файла (имя, путь, комментарий).
 * @returns {Promise<void>}
 */
export async function saveFileChanges() {
    const name = document.getElementById("detail-name").value;
    const path = document.getElementById("detail-path").value;
    const comment = document.getElementById("detail-comment").value;

    try {
        if (!currentFileId) {
            alert("Файл не выбран.");
            return;
        }

        await updateFile(currentFileId, { name, path, comment });

        const files = await fetchFiles();
        renderTable(files, handlers);

        bootstrap.Modal.getInstance(document.getElementById("fileDetailModal")).hide();
    } catch (error) {
        console.error("Ошибка при сохранении изменений:", error);
        alert("Не удалось сохранить изменения.");
    }
}

/**
 * Выполняет актуализацию файлов (синхронизацию с БД).
 * @returns {Promise<void>}
 */
export async function actualize() {
    try {
        const data = await actualizeFiles();

        alert(`Добавлено: ${data.added}, Удалено: ${data.removed}`);
        if (data.added > 0 || data.removed > 0) {
            const files = await fetchFiles();
            renderTable(files, handlers);
        }
    } catch (error) {
        console.error("Ошибка при актуализации:", error);
        alert("Произошла ошибка при актуализации.");
    }
}
// Получаем DOM-элемент модального окна загрузки файла
const uploadModal = document.getElementById("uploadModal");
// Получаем DOM-элемент формы загрузки файла
const uploadForm = document.getElementById("uploadForm");

/**
 * Обработчик события отправки формы загрузки файла.
 * Отменяет стандартное поведение формы, загружает файл через API,
 * закрывает модальное окно, сбрасывает форму и обновляет таблицу файлов.
 *
 * @param {SubmitEvent} e - Событие отправки формы
 * @returns {Promise<void>}
 */
uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    try {
        // Загружаем файл на сервер, передавая форму с данными
        await uploadFile(uploadForm);
        // Закрываем модальное окно загрузки файла
        bootstrap.Modal.getInstance(uploadModal).hide();
        // Сбрасываем форму, очищая все поля
        uploadForm.reset();
        // Получаем обновленный список файлов с сервера
        const files = await fetchFiles();
        // Перерисовываем таблицу с обновленными данными
        renderTable(files, handlers);
    } catch (error) {
        // Логируем ошибку в консоль и показываем пользователю
        console.error(error);
        alert(`Ошибка при загрузке: ${error.message}`);
    }
});

/**
 * Обработчики событий для работы с файлами.
 * @type {{ openFileDetails: Function, deleteFile: Function }}
 */
export const handlers = {
    openFileDetails,
    deleteFile
};
