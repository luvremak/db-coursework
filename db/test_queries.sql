-- ============================================
-- test_queries.sql
-- Набір тестових запитів для перевірки БД
-- ============================================

-- 1. Вибрати всі проєкти з командами
SELECT p.ProjectID, p.ProjectName, t.TeamName
FROM Project p
LEFT JOIN Team t ON p.TeamID = t.TeamID;

-- 2. Список усіх задач разом із бордами та проєктами
SELECT 
    task.TaskID,
    task.Title,
    task.Status,
    task.Priority,
    board.BoardName,
    project.ProjectName
FROM Task task
JOIN Board board ON task.BoardID = board.BoardID
JOIN Project project ON board.ProjectID = project.ProjectID;

-- 3. Завдання з тегами
SELECT 
    t.TaskID,
    t.Title,
    tg.TagName,
    tg.Color
FROM Task t
JOIN Task_Tag tt ON t.TaskID = tt.TaskID
JOIN Tag tg ON tt.TagID = tg.TagID
ORDER BY t.TaskID;

-- 4. Завдання з виконавцями
SELECT 
    t.TaskID,
    t.Title,
    u.FullName AS Assignee
FROM Task t
JOIN Task_Assignee ta ON t.TaskID = ta.TaskID
JOIN "User" u ON ta.UserID = u.UserID
ORDER BY t.TaskID;

-- 5. Коментарі із зазначенням користувача, задачі і часу
SELECT 
    c.CommentID,
    c.Content,
    c.CreatedAt,
    u.FullName,
    t.Title
FROM Comment c
JOIN "User" u ON c.UserID = u.UserID
JOIN Task t ON c.TaskID = t.TaskID
ORDER BY c.CreatedAt DESC;

-- 6. Агрегація: кількість задач у кожному борді
SELECT board.BoardName, COUNT(task.TaskID) AS TaskCount
FROM Board board
LEFT JOIN Task task ON board.BoardID = task.BoardID
GROUP BY board.BoardID;

-- 7. Агрегація: кількість користувачів у кожній команді
SELECT 
    team.TeamName,
    COUNT(tu.UserID) AS Members
FROM Team team
LEFT JOIN Team_User tu ON team.TeamID = tu.TeamID
GROUP BY team.TeamID;

-- 8. Агрегація: кількість задач по пріоритету
SELECT Priority, COUNT(*) AS Total
FROM Task
GROUP BY Priority;

-- 9. Завдання, дедлайн яких менший ніж 30 днів від сьогодні
SELECT * FROM Task
WHERE DueDate < CURRENT_DATE + INTERVAL '30 days';

-- 10. Усі активні проєкти (EndDate IS NULL)
SELECT * FROM Project WHERE EndDate IS NULL;

-- 11. Перевірка каскаду: видалити борд → видаляються задачі
-- (Просто подивитися, скільки задач з BoardID=4 перед видаленням)
SELECT * FROM Task WHERE BoardID = 4;

-- 12. Видалення для тесту каскаду (не запускається за замовчуванням)
-- DELETE FROM Board WHERE BoardID = 4;

-- 13. Перевірка каскаду: видалення користувача видалить його коментарі
SELECT * FROM Comment WHERE UserID = 1;

-- 14. Вибрати всіх користувачів з їх ролями у різних проєктах
SELECT 
    u.FullName,
    p.ProjectName,
    pu.Role
FROM "User" u
JOIN Project_User pu ON u.UserID = pu.UserID
JOIN Project p ON pu.ProjectID = p.ProjectID
ORDER BY u.FullName;

-- 15. Вибрати всі задачі з повною інформацією:
-- проект, борд, виконавці, теги
SELECT 
    t.TaskID,
    t.Title,
    b.BoardName,
    p.ProjectName,
    STRING_AGG(DISTINCT u.FullName, ', ') AS Assignees,
    STRING_AGG(DISTINCT tg.TagName, ', ') AS Tags
FROM Task t
JOIN Board b ON t.BoardID = b.BoardID
JOIN Project p ON b.ProjectID = p.ProjectID
LEFT JOIN Task_Assignee ta ON t.TaskID = ta.TaskID
LEFT JOIN "User" u ON ta.UserID = u.UserID
LEFT JOIN Task_Tag tt ON t.TaskID = tt.TaskID
LEFT JOIN Tag tg ON tt.TagID = tg.TagID
GROUP BY t.TaskID, b.BoardID, p.ProjectID
ORDER BY t.TaskID;

-- 16. Знайти задачі без виконавців
SELECT * FROM Task t
WHERE NOT EXISTS (
    SELECT 1 FROM Task_Assignee ta WHERE ta.TaskID = t.TaskID
);

-- 17. Знайти користувачів, які не прив’язані до жодної команди
SELECT u.*
FROM "User" u
LEFT JOIN Team_User tu ON u.UserID = tu.UserID
WHERE tu.TeamID IS NULL;

-- 18. Знайти команди, які працюють одночасно над кількома проєктами
SELECT 
    team.TeamName,
    COUNT(project.ProjectID) AS Projects
FROM Team team
JOIN Project project ON project.TeamID = team.TeamID
GROUP BY team.TeamID
HAVING COUNT(project.ProjectID) > 1;

-- 19. Дерева зв’язків: проект → борди → задачі
SELECT 
    p.ProjectName,
    b.BoardName,
    t.Title AS TaskTitle
FROM Project p
LEFT JOIN Board b ON p.ProjectID = b.ProjectID
LEFT JOIN Task t ON b.BoardID = t.BoardID
ORDER BY p.ProjectName, b.BoardID, t.TaskID;

-- 20. Топ-3 користувачі за кількістю призначених задач
SELECT 
    u.FullName,
    COUNT(ta.TaskID) AS AssignedTasks
FROM "User" u
JOIN Task_Assignee ta ON u.UserID = ta.UserID
GROUP BY u.UserID
ORDER BY AssignedTasks DESC
LIMIT 3;
