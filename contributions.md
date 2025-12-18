# Contributions

## Features

| Commit                         | Description                                                    | Contributor  |
| ------------------------------ | -------------------------------------------------------------- | ------------ |
| feat: core                     | Створення базової архітектури (репозиторії, сервіси).        | Анна         |
| feat: add Company module       | Реалізація базового модуля компаній.                           | Анна         |
| feat: add Employee module      | Реалізація модуля для роботи з персоналом.                     | Дар'я        |
| feat: add Project module       | Реалізація модуля для управління проектами.                    | Дар'я        |
| feat: add Task module          | Реалізація системи задач.                                      | Дар'я        |
| feat: add TimeTracking module  | Система обліку витраченого часу.                               | Анна         |
| feat: add code / owner_tg_id   | Додавання ідентифікаторів для Компаній.                        | Дар'я        |
| feat: add is_admin flag        | Впровадження прав адміністратора для співробітників.           | Анна         |
| feat: pagination support       | Підтримка пагінації у списках бота.                            | Анна         |
| feat: add service instances    | Ініціалізація сервісів для всіх модулів.                       | Дар'я        |
| feat: 3-letter code to Project | Генерація коротких кодів для проектів.                         | Дар'я        |
| feat: tg bot support           | "Інтеграція модулів (Company, Project, Employee, Task) у бот." | Анна / Дар'я |
| feat: alembic                  | Налаштування системи міграцій бази даних.                      | Дар'я        |
| feat: time tracking for tasks  | Запуск функціоналу відстеження часу.                           | Дар'я        |
| feat: task status / keyboard   | Керування статусами завдань через кнопки.                      | Анна         |
| feat: task shortcut            | Швидкий доступ до завдань за ID.                               | Дар'я        |
| feat: display tracked time     | Відображення накопиченого часу в деталях.                      | Анна         |
| feat: CSV export               | Експорт статистики компанії у файл.                            | Анна         |
| feat: docker                   | Створення Docker-контейнерів для розгортання.                  | Дар'я        |

---

## Fixes

| Commit                   | Description                                              | Contributor |
| ------------------------ | -------------------------------------------------------- | ----------- |
| fix: on delete cascade   | Виправлення цілісності даних при видаленні сутностей.    | Дар'я       |
| fix: tg id is BigInteger | Виправлення типу даних для підтримки довгих Telegram ID. | Дар'я       |
| fix: tests db usage      | Усунення помилок при підключенні тестів до БД.           | Дар'я       |
| fix: tests               | Фінальне налагодження автоматичних тестів.               | Дар'я       |

---

## Database Migrations

| Commit                              | Description                                  | Contributor |
| ----------------------------------- | -------------------------------------------- | ----------- |
| migration: company/project/employee | Створення початкових таблиць у БД.           | Анна        |
| migration: on delete cascade        | Оновлення зв'язків для каскадного видалення. | Анна        |
| migration: task status              | Додавання поля статусу до таблиці задач.     | Анна        |
| migration: time tracking            | Створення таблиці для записів часу.          | Дар'я       |
| migration: add indexes              | Оптимізація бази даних (створення індексів). | Дар'я       |

---

## Documentation and SQL

| Commit              | Description                                         | Contributor |
| ------------------- | --------------------------------------------------- | ----------- |
| docs: schema        | Документування ER-схеми бази даних.                 | Анна        |
| docs: queries       | Опис та підготовка SQL-запитів для звіту.           | Анна        |
| sql: employee stats | Створення запиту для аналізу роботи співробітників. | Анна        |
| sql: project stats  | Створення запиту для аналізу прогресу проектів.     | Дар'я       |
| docs                | Загальні правки документації проекту.               | Дар'я       |

---

## Refactoring, Testing, and Maintenance

| Commit                              | Description                                      | Contributor  |
| ----------------------------------- | ------------------------------------------------ | ------------ |
| refactor: inline repo instantiation | Спрощення коду ініціалізації репозиторіїв.       | Дар'я        |
| refactor: add logging               | Впровадження логування для відстеження роботи.   | Анна         |
| test: company/employee/project      | Написання модульних тестів для перевірки логіки. | Анна / Дар'я |
| logs: log sql queries               | Додавання виводу SQL-запитів у консоль.          | Анна         |
| update/add requirements.txt         | Керування залежностями проекту.                  | Анна / Дар'я |
