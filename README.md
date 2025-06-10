# 📁 File Storage Organizer — веб-приложение на Flask

Веб-приложение для управления файлами в локальном хранилище (`storage/`) с помощью веб-интерфейса и базы данных PostgreSQL. Поддерживает загрузку, скачивание, удаление, редактирование и синхронизацию файлов.

---

## ✅ Функциональные возможности

### 🎯 Основной функционал:
- Получение списка всех файлов (из базы данных)
- Просмотр информации о конкретном файле
- Загрузка новых файлов с сохранением в БД и на диск
- Удаление файлов (и из хранилища, и из базы)
- Редактирование информации о файле (имя, путь, комментарий)
- Скачивание файлов по HTTP
- Синхронизация файловой системы и БД (добавление новых / удаление отсутствующих)

---

## 💡 Архитектурные принципы

### 🔧 Слой бизнес-логики:
Проект построен по паттерну **Service Layer**:

- `FileService` — отвечает за всю бизнес-логику приложения. Вызывает методы репозитория и менеджера хранилища.
- `FileRepository` — реализует взаимодействие с базой данных (CRUD), изолируя SQLAlchemy.
- `StorageManager` — управляет файлами в директории `storage/`: сохранение, удаление, переименование, сканирование.

Такое разделение облегчает тестирование, сопровождение и расширение проекта.

### 🧱 MVC:
- **Model**: `FileRecord` (SQLAlchemy)
- **View**: HTML-шаблоны + Bootstrap + JavaScript
- **Controller**: `views.py` (Flask route-функции)

---

## 📦 Структура проекта

```
.
├── docker-compose.yml                  # Конфигурация Docker Compose
├── Dockerfile                          # Dockerfile для Flask-приложения
├── requirements.txt                    # Зависимости Python
├── .env                                # Файл с переменными окружения (не коммитится)
├── .env.example                        # Шаблон для .env
└── src/                                # Исходный код приложения
    ├── __init__.py
    ├── app.py                          # Точка входа
    ├── config.py                       # Класс Config с настройками Flask
    ├── models.py                       # SQLAlchemy модели
    ├── views.py                        # роуты и функции представления
    ├── templates/                      # HTML-шаблоны
    ├── static/                         # CSS, JS и изображения
    ├── storage/                        # Файлы, отслеживаемые системой
    └── services/                       # Бизнес-логика и вспомогательные модули
        ├── file_service.py
        ├── file_repository.py
        ├── storage_manager.py
        └── path_service.py
```

---

## 🚀 Быстрый старт (через Docker)

```bash
git clone https://github.com/PsYcHo-DiSs/file_storage_organizer_v2.git
cd file_storage_organizer_v2
cp .env.example .env
docker-compose up --build
```

Открой в браузере: http://localhost:5000

---

## ⚙️ .env переменные

```env
SQLALCHEMY_DATABASE_URI=postgresql://postgres:123321@localhost:5654/file_storage
SECRET_KEY=75_57_75
WTF_CSRF_ENABLED=True
FLASK_DEBUG=False
SQLALCHEMY_ECHO=False
```

---

## 🐳 Docker-описание

| Сервис | Назначение         | Порт  | Комментарий |
|--------|--------------------|-------|-------------|
| db     | PostgreSQL 15      | 5654  | С volume |
| app    | Flask-приложение   | 5000  | Стартует после БД |

---

## 🧪 Альтернативный запуск (без Docker)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.app
```

---

## 🔁 Возможности

- Синхронизация хранилища и БД по кнопке
- Просмотр и фильтрация файлов
- Редактирование метаданных
- Скачивание / удаление
- Загрузка файлов

---

## 🧠 Используемые технологии

**Backend**: Python, Flask, SQLAlchemy, PostgreSQL  
**Frontend**: Bootstrap, JavaScript (fetch API, модульный стиль)  
**Инфраструктура**: Docker, Compose

---

## 💬 Ответы

**Сроки**: около 7 дней работы  
**Зачем паттерны**: отделение логики от инфраструктуры  
**Что улучшено**: расширяемость, тестируемость, читаемость