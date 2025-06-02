/**
 * Получает список всех файлов с сервера.
 * @returns {Promise<Array<Object>>} Список файлов в формате JSON
 */
export async function fetchFiles() {
    const response = await fetch(`/files`);
    return await response.json();
}

/**
 * Удаляет файл по ID.
 * @param {number} id - ID файла
 * @returns {Promise<Response>} Ответ от сервера
 */
export async function deleteFile(id) {
    return await fetch(`/files/${id}/delete`, { method: 'DELETE' });
}

/**
 * Получает подробную информацию о файле по ID.
 * @param {number} id - ID файла
 * @returns {Promise<Object>} Детали файла
 */
export async function fetchFileDetail(id) {
    const response = await fetch(`/files/${id}`);
    return await response.json();
}

/**
 * Обновляет данные о файле.
 * @param {number} id - ID файла
 * @param {Object} data - Объект с новыми данными
 * @param {string} [data.name] - Новое имя
 * @param {string} [data.path] - Новый путь
 * @param {string} [data.comment] - Комментарий
 * @returns {Promise<Response>} Ответ от сервера
 */
export async function updateFile(id, data) {
    return await fetch(`/files/${id}/update`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
}

/**
 * Актуализирует базу данных: добавляет/удаляет записи.
 * @returns {Promise<Object>} Количество добавленных и удалённых файлов
 */
export async function actualizeFiles() {
    const response = await fetch(`/actualize`, { method: "POST" });
    return await response.json();
}

/**
 * Загружает файл на сервер через форму.
 * @param {HTMLFormElement} formElement - Элемент формы с данными файла
 * @throws {Error} Если загрузка завершилась с ошибкой, выбрасывает исключение с сообщением
 * @returns {Promise<Object>} Ответ сервера с результатом загрузки
 */
export async function uploadFile(formElement) {
  const formData = new FormData(formElement);

  const response = await fetch(`/files/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || "Ошибка загрузки файла");
  }

  return await response.json();
}