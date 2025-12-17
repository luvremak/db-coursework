# Time Tracking Bot

Система проектного менеджменту та трекінгу часу з Telegram-ботом.


## Технології

- Python 3.13
- SQLAlchemy (ORM)
- aiogram (Telegram Bot)
- PostgreSQL
- pytest (тестування)

## Налаштування

1. Клонуйте репозиторій:
```bash
git clone <repository-url>
cd <repository>
```

2. Створіть `.env.docker`:
```env
POSTGRES_DB=time_tracking_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
TG_BOT_TOKEN=your_telegram_bot_token
```

3. Запустіть сервіси:
```bash
docker-compose up -d
```

## Запуск

**Docker:**
```bash
docker-compose up -d
```

## Тестування

```bash
pytest                              # всі тести
pytest tests/test_project/          # тести модуля
pytest tests/test_company/test_company_services.py  # конкретний файл
```

## Структура проєкту

```
app/
├── core/
│   ├── database.py      # підключення до БД
│   ├── models.py        # базова модель
│   ├── settings.py      # конфігурація
│   ├── repo_base.py     # базовий репозиторій
│   ├── crud_base.py     # базовий CRUD
│   ├── serializer.py    # серіалізація даних
│   └── exceptions.py    # помилки
├── company/
│   ├── tables.py        # SQLAlchemy таблиця
│   ├── models.py        # бізнес-моделі
│   ├── dal.py           # data access layer
│   ├── services.py      # бізнес-логіка
│   └── exceptions.py    # помилки
├── project/             # управління проектами
├── task/                # управління задачами
├── employee/            # управління співробітниками
├── time_tracking/       # облік робочого часу
└── tg_bot/              # Telegram-бот
tests/                   # тести
docs/                    # документація
```
