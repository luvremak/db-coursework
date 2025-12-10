-- ================================
--     CREATE TABLES
-- ================================

CREATE TABLE "User" (
    UserID SERIAL PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL
);

CREATE TABLE Team (
    TeamID SERIAL PRIMARY KEY,
    TeamName VARCHAR(100) NOT NULL,
    Description TEXT
);

CREATE TABLE Project (
    ProjectID SERIAL PRIMARY KEY,
    ProjectName VARCHAR(100) NOT NULL,
    Description TEXT,
    StartDate DATE NOT NULL,
    EndDate DATE,
    TeamID INT REFERENCES Team(TeamID) ON DELETE SET NULL
);

CREATE TABLE Board (
    BoardID SERIAL PRIMARY KEY,
    BoardName VARCHAR(100) NOT NULL,
    ProjectID INT REFERENCES Project(ProjectID) ON DELETE CASCADE
);

CREATE TABLE Task (
    TaskID SERIAL PRIMARY KEY,
    Title VARCHAR(150) NOT NULL,
    Description TEXT,
    Status VARCHAR(50) DEFAULT 'To Do',
    Priority VARCHAR(20) CHECK (Priority IN ('Low','Medium','High')),
    DueDate DATE,
    BoardID INT REFERENCES Board(BoardID) ON DELETE CASCADE
);

CREATE TABLE Comment (
    CommentID SERIAL PRIMARY KEY,
    Content TEXT NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UserID INT REFERENCES "User"(UserID) ON DELETE CASCADE,
    TaskID INT REFERENCES Task(TaskID) ON DELETE CASCADE
);

CREATE TABLE Tag (
    TagID SERIAL PRIMARY KEY,
    TagName VARCHAR(50) NOT NULL,
    Color VARCHAR(20)
);

CREATE TABLE Task_Assignee (
    UserID INT REFERENCES "User"(UserID) ON DELETE CASCADE,
    TaskID INT REFERENCES Task(TaskID) ON DELETE CASCADE,
    PRIMARY KEY (UserID, TaskID)
);

CREATE TABLE Task_Tag (
    TaskID INT REFERENCES Task(TaskID) ON DELETE CASCADE,
    TagID INT REFERENCES Tag(TagID) ON DELETE CASCADE,
    PRIMARY KEY (TaskID, TagID)
);

CREATE TABLE Project_User (
    ProjectID INT REFERENCES Project(ProjectID) ON DELETE CASCADE,
    UserID INT REFERENCES "User"(UserID) ON DELETE CASCADE,
    Role VARCHAR(50) NOT NULL,
    PRIMARY KEY (ProjectID, UserID)
);

CREATE TABLE Team_User (
    TeamID INT REFERENCES Team(TeamID) ON DELETE CASCADE,
    UserID INT REFERENCES "User"(UserID) ON DELETE CASCADE,
    Role VARCHAR(50) NOT NULL, 
    PRIMARY KEY (TeamID, UserID)
);


-- ================================
--        INSERT DATA
-- ================================

-- Users
INSERT INTO "User" (FullName, Email, PasswordHash) VALUES
('Анна Коваль', 'anna.koval@example.com', 'hash123'),
('Ігор Романюк', 'romanuk.ihor@example.com', 'hash234'),
('Марія Левчук', 'maria.levchuk@example.com', 'hash345'),
('Дмитро Савчук', 'd.savchuk@example.com', 'hash456'),
('Олена Гринюк', 'olena.gry@example.com', 'hash567');

-- Teams
INSERT INTO Team (TeamName, Description) VALUES
('Alpha Team', 'Основна команда розробки'),
('Design Squad', 'Команда UX/UI дизайнерів'),
('QA Force', 'Команда тестування');

-- Projects
INSERT INTO Project (ProjectName, Description, StartDate, EndDate, TeamID) VALUES
('AeroTaxi Platform', 'Система замовлення аеротаксі', '2024-06-01', NULL, 1),
('Mobile Redesign', 'Редизайн мобільного застосунку', '2024-03-10', '2024-12-01', 2),
('Testing Automation', 'Автоматизація QA процесів', '2024-01-15', NULL, 3);

-- Boards
INSERT INTO Board (BoardName, ProjectID) VALUES
('Backlog', 1),
('Development', 1),
('Design Tasks', 2),
('QA Pipeline', 3);

-- Tasks
INSERT INTO Task (Title, Description, Status, Priority, DueDate, BoardID) VALUES
('API для бронювання рейсів', 'Розробити REST API для бронювання', 'In Progress', 'High', '2024-12-30', 2),
('UI макети головної сторінки', 'Створити Figma прототипи', 'To Do', 'Medium', '2024-11-15', 3),
('Налаштувати CI/CD', 'Інтеграція GitHub Actions', 'In Review', 'High', '2024-12-10', 4),
('Написати автотести для API', 'Створити тестовий набір Postman', 'To Do', 'Low', '2025-01-10', 4),
('Модуль авторизації', 'Додати підтримку JWT', 'Done', 'Medium', '2024-09-01', 2);

-- Comments
INSERT INTO Comment (Content, UserID, TaskID) VALUES
('Потрібно уточнити бізнес-логіку з клієнтом', 1, 1),
('Готовий чорновий варіант макета', 3, 2),
('Додав новий тест-кейс', 2, 3),
('Помилка відтворюється стабільно', 5, 4);

-- Tags
INSERT INTO Tag (TagName, Color) VALUES
('Backend', '#FF5733'),
('Frontend', '#33C1FF'),
('Urgent', '#FF0000'),
('Research', '#8D33FF');

-- Task Assignees
INSERT INTO Task_Assignee (UserID, TaskID) VALUES
(1, 1),
(2, 1),
(3, 2),
(5, 3),
(2, 4),
(4, 5);

-- Task Tags
INSERT INTO Task_Tag (TaskID, TagID) VALUES
(1, 1),
(1, 3),
(2, 2),
(3, 1),
(3, 3),
(4, 4),
(5, 1);

-- Project Users
INSERT INTO Project_User (ProjectID, UserID, Role) VALUES
(1, 1, 'Project Manager'),
(1, 2, 'Backend Developer'),
(1, 4, 'DevOps Engineer'),
(2, 3, 'UI/UX Designer'),
(3, 5, 'QA Engineer');

-- Team Users
INSERT INTO Team_User (TeamID, UserID, Role) VALUES
(1, 1, 'Lead'),
(1, 2, 'Developer'),
(1, 4, 'DevOps'),
(2, 3, 'Designer'),
(3, 5, 'QA Analyst');
