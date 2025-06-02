/**
 * Отрисовывает таблицу файлов на странице.
 *
 * @param {Array<Object>} files - Массив объектов файлов, каждый объект должен содержать поля:
 *                                id, name, extension, size, path, created_at.
 * @param {Object} handlers - Объект с обработчиками событий для элементов таблицы.
 * @param {function(number|string): void} handlers.openFileDetails - Функция для открытия деталей файла по ID.
 * @param {function(number|string): void} handlers.deleteFile - Функция для удаления файла по ID.
 */
export function renderTable(files, handlers) {
    const tbody = document.getElementById("files-body");
    tbody.innerHTML = ``;

    files.forEach(file => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td><a href="#" class="file-link" data-id="${file.id}">${file.name}</a></td>
            <td>${file.extension}</td>
            <td>${file.size}</td>
            <td>storage: ${file.path}</td>
            <td>${file.created_at}</td>
            <td>
                <button class="btn btn-sm btn-primary detail-btn" data-id="${file.id}">Подробнее</button>
                <button class="btn btn-sm btn-danger delete-btn" data-id="${file.id}">Удалить</button>
            </td>
        `;
        tbody.appendChild(row);
    });

    // Назначаем обработчики кликов для ссылок и кнопок "Подробнее"
    tbody.querySelectorAll(".file-link, .detail-btn").forEach(el =>
        el.addEventListener("click", (e) => {
            e.preventDefault();
            const id = el.dataset.id;
            handlers.openFileDetails(id);
        })
    );

    // Назначаем обработчики кликов для кнопок "Удалить"
    tbody.querySelectorAll(".delete-btn").forEach(el =>
        el.addEventListener("click", () => {
            const id = el.dataset.id;
            handlers.deleteFile(id);
        })
    );
}
