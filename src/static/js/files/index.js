import { fetchFiles } from "./api.js";
import { renderTable } from "./render.js";
import { actualize, saveFileChanges, handlers } from "./actions.js";

/**
 * Инициализация интерфейса приложения.
 * Загружает список файлов, отображает их,
 * навешивает обработчики событий для поиска, актуализации, сохранения, удаления и скачивания.
 */
document.addEventListener("DOMContentLoaded", async () => {
    const searchNameInput = document.getElementById("searchName");
    const searchPathInput = document.getElementById("searchPath");
    const actualizeBtn = document.getElementById("actualize-btn");
    const saveBtn = document.getElementById("save-detail-btn");
    const deleteBtn = document.getElementById("modal-delete-btn");
    const downloadBtn = document.getElementById("modal-download-btn");

    // Загружаем все файлы и отрисовываем таблицу
    let allFiles = await fetchFiles();
    renderTable(allFiles, handlers);

    /**
     * Функция фильтрации и обновления таблицы по значениям поиска.
     * Выполняется при вводе в поля поиска имени и пути.
     */
    function applySearch() {
        const nameQuery = searchNameInput.value.toLowerCase();
        const pathQuery = searchPathInput.value.toLowerCase();
        const filtered = allFiles.filter(file =>
        file.name.toLowerCase().includes(nameQuery) &&
        file.path.toLowerCase().includes(pathQuery)
        );
        renderTable(filtered, handlers);
    }
    // Навешиваем обработчики ввода для фильтрации
    searchNameInput.addEventListener("input", applySearch);
    searchPathInput.addEventListener("input", applySearch);

    // Кнопка актуализации файлов (синхронизация с сервером)
    if (actualizeBtn) {
        actualizeBtn.addEventListener("click", async () => {
            await actualize();
            allFiles = await fetchFiles(); // обновляем для поиска
        });
    }

    // Кнопка сохранения изменений в деталях файла
    if (saveBtn) {
        saveBtn.addEventListener("click", async () => {
            await saveFileChanges();
            allFiles = await fetchFiles(); // чтобы после сохранения поиск по новым данным работал
        });
    }

    // Кнопка удаления файла из модального окна
    if (deleteBtn) {
        deleteBtn.addEventListener("click", () => {
            handlers.deleteFile(window.currentFileId);
        });
    }

    // Кнопка удаления файла из модального окна
    if (downloadBtn) {
        downloadBtn.addEventListener("click", () => {
            if (window.currentFileId) {
                window.location.href = `/files/${window.currentFileId}/download`;
            }
        });
    }
});
