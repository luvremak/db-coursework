-- ============================================
-- test_queries.sql
-- Набір тестових запитів для перевірки БД
-- ============================================

-- 1.1 Сценарій: Створення нового проєкту з бордами, початковими задачами та призначенням команди
DO $$
DECLARE
    v_team_id INT := 1;  
    v_project_name VARCHAR(100) := 'Smart Logistics System';
    v_owner_id INT := 1;  
    v_project_id INT;
    v_backlog_board_id INT;
    v_sprint_board_id INT;
    v_review_board_id INT;
    v_completed_board_id INT;
    v_setup_task_id INT;
    v_requirements_task_id INT;
    v_design_task_id INT;
    v_backend_tag INT;
    v_frontend_tag INT;
    team_exists BOOLEAN;
    user_in_team BOOLEAN;
    duplicate_project BOOLEAN;
BEGIN
    -- Валідація вхідних даних
    -- Перевірка 1: Чи існує команда
    SELECT EXISTS(SELECT 1 FROM Team WHERE TeamID = v_team_id) INTO team_exists;
    IF NOT team_exists THEN
        RAISE EXCEPTION 'Team with ID % does not exist', v_team_id;
    END IF;
    
    -- Перевірка 2: Чи користувач є членом команди
    SELECT EXISTS(
        SELECT 1 FROM Team_User 
        WHERE TeamID = v_team_id AND UserID = v_owner_id
    ) INTO user_in_team;
    IF NOT user_in_team THEN
        RAISE EXCEPTION 'User % is not a member of team %', v_owner_id, v_team_id;
    END IF;
    
    -- Перевірка 3: Чи немає дублікатів назви проєкту в команді
    SELECT EXISTS(
        SELECT 1 FROM Project 
        WHERE ProjectName = v_project_name 
          AND TeamID = v_team_id 
          AND EndDate IS NULL
    ) INTO duplicate_project;
    IF duplicate_project THEN
        RAISE EXCEPTION 'Active project with name "%" already exists in this team', v_project_name;
    END IF;

    -- Створення проєкту
    INSERT INTO Project (ProjectName, Description, StartDate, EndDate, TeamID)
    VALUES (
        v_project_name,
        'Удосконалена система управління логістикою з оптимізацією маршрутів на основі штучного інтелекту',
        CURRENT_DATE,
        NULL,
        v_team_id
    )
    RETURNING ProjectID INTO v_project_id;

    RAISE NOTICE 'Created project with ID: %', v_project_id;

    -- Призначення учасників проєкту
    INSERT INTO Project_User (ProjectID, UserID, Role)
    VALUES 
        (v_project_id, 1, 'Project Manager'), 
        (v_project_id, 2, 'Backend Developer'),
        (v_project_id, 4, 'DevOps Engineer'); 

    -- Створення стандартних бордів
    INSERT INTO Board (BoardName, ProjectID)
    VALUES 
        ('Backlog', v_project_id)
    RETURNING BoardID INTO v_backlog_board_id;
    
    INSERT INTO Board (BoardName, ProjectID)
    VALUES 
        ('Sprint 1', v_project_id)
    RETURNING BoardID INTO v_sprint_board_id;
    
    INSERT INTO Board (BoardName, ProjectID)
    VALUES 
        ('In Review', v_project_id)
    RETURNING BoardID INTO v_review_board_id;
    
    INSERT INTO Board (BoardName, ProjectID)
    VALUES 
        ('Completed', v_project_id)
    RETURNING BoardID INTO v_completed_board_id;

    RAISE NOTICE 'Created 4 boards: %, %, %, %', v_backlog_board_id, v_sprint_board_id, v_review_board_id, v_completed_board_id;

    -- Створення початкових задач у Backlog
    INSERT INTO Task (Title, Description, Status, Priority, DueDate, BoardID)
    VALUES (
        'Налаштування інфраструктури проекту',
        'Ініціалізація репозиторію, конвеєра CI/CD та середовища розробки',
        'To Do',
        'High',
        CURRENT_DATE + INTERVAL '7 days',
        v_backlog_board_id
    )
    RETURNING TaskID INTO v_setup_task_id;
    
    INSERT INTO Task (Title, Description, Status, Priority, DueDate, BoardID)
    VALUES (
        'Збір вимог',
        'Документуйте функціональні та нефункціональні вимоги',
        'To Do',
        'High',
        CURRENT_DATE + INTERVAL '14 days',
        v_backlog_board_id
    )
    RETURNING TaskID INTO v_requirements_task_id;
    
    INSERT INTO Task (Title, Description, Status, Priority, DueDate, BoardID)
    VALUES (
        'Архітектурний дизайн',
        'Архітектура системи проектування та схема бази даних',
        'To Do',
        'Medium',
        CURRENT_DATE + INTERVAL '21 days',
        v_backlog_board_id
    )
    RETURNING TaskID INTO v_design_task_id;

    RAISE NOTICE 'Created 3 initial tasks: %, %, %', v_setup_task_id, v_requirements_task_id, v_design_task_id;

    -- Призначення задач членам команди
    INSERT INTO Task_Assignee (TaskID, UserID)
    VALUES 
        (v_setup_task_id, 4),        
        (v_requirements_task_id, 1),
        (v_design_task_id, 2);       

    -- Отримання існуючих тегів або використання нових ID
    SELECT TagID INTO v_backend_tag FROM Tag WHERE TagName = 'Backend' LIMIT 1;
    SELECT TagID INTO v_frontend_tag FROM Tag WHERE TagName = 'Frontend' LIMIT 1;

    -- Прив'язка тегів до задач
    IF v_backend_tag IS NOT NULL THEN
        INSERT INTO Task_Tag (TaskID, TagID)
        VALUES 
            (v_setup_task_id, v_backend_tag),
            (v_design_task_id, v_backend_tag);
    END IF;

    -- Створення початкового коментаря від PM
    INSERT INTO Comment (Content, UserID, TaskID)
    VALUES (
        'Заплановано стартову зустріч проєкту. Почнемо з налаштування інфраструктури та аналізу вимог..',
        1, 
        v_setup_task_id
    );

    -- Повернення повної інформації про створений проєкт
    RAISE NOTICE '=== PROJECT CREATION SUMMARY ===';
    RAISE NOTICE 'Project: % (ID: %)', v_project_name, v_project_id;
    RAISE NOTICE 'Team: Alpha Team';
    RAISE NOTICE 'Boards created: 4 (Backlog, Sprint 1, In Review, Completed)';
    RAISE NOTICE 'Initial tasks: 3';
    RAISE NOTICE 'Team members assigned: 3';
    RAISE NOTICE 'Status: Successfully created';

EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Duplicate entry detected: %', SQLERRM;
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'Referenced entity does not exist: %', SQLERRM;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Project creation failed: %', SQLERRM;
END $$;

SELECT 
    p.ProjectID,
    p.ProjectName,
    p.StartDate,
    t.TeamName,
    COUNT(DISTINCT b.BoardID) as BoardsCreated,
    COUNT(DISTINCT task.TaskID) as InitialTasks,
    COUNT(DISTINCT pu.UserID) as TeamMembers
FROM Project p
JOIN Team t ON p.TeamID = t.TeamID
LEFT JOIN Board b ON p.ProjectID = b.ProjectID
LEFT JOIN Task task ON b.BoardID = task.BoardID
LEFT JOIN Project_User pu ON p.ProjectID = pu.ProjectID
WHERE p.ProjectName = 'Smart Logistics System'
GROUP BY p.ProjectID, p.ProjectName, p.StartDate, t.TeamName;


-----------------------------------------------------------------------------------------------------------------
-- 1.2 -- Сценарій: Створення складної задачі з підзадачами, тегами, виконавцями та коментарем
DO $$
DECLARE
    v_board_id INT := 2; 
    v_task_title VARCHAR(150) := 'Payment Integration System';
    v_assignee_ids INT[] := ARRAY[2, 4];  
    v_main_task_id INT;
    v_subtask1_id INT;
    v_subtask2_id INT;
    v_subtask3_id INT;
    v_subtask4_id INT;
    v_backend_tag INT;
    v_urgent_tag INT;
    board_exists BOOLEAN;
    board_project_active BOOLEAN;
    assignee_count INT;
    invalid_assignees INT;
    i INT;
BEGIN
    -- Валідація вхідних даних
    -- Перевірка 1: Чи існує борд
    SELECT EXISTS(SELECT 1 FROM Board WHERE BoardID = v_board_id) INTO board_exists;
    IF NOT board_exists THEN
        RAISE EXCEPTION 'Board with ID % does not exist', v_board_id;
    END IF;
    
    -- Перевірка 2: Чи проєкт борду активний
    SELECT EXISTS(
        SELECT 1 FROM Board b
        JOIN Project p ON b.ProjectID = p.ProjectID
        WHERE b.BoardID = v_board_id AND p.EndDate IS NULL
    ) INTO board_project_active;
    IF NOT board_project_active THEN
        RAISE EXCEPTION 'Cannot create task in completed project';
    END IF;
    
    -- Перевірка 3: Чи всі виконавці є членами проєкту
    SELECT COUNT(*) INTO assignee_count FROM unnest(v_assignee_ids) AS uid;
    
    SELECT COUNT(*) INTO invalid_assignees
    FROM unnest(v_assignee_ids) AS uid
    WHERE NOT EXISTS (
        SELECT 1 FROM Project_User pu
        JOIN Board b ON pu.ProjectID = b.ProjectID
        WHERE b.BoardID = v_board_id AND pu.UserID = uid
    );
    
    IF invalid_assignees > 0 THEN
        RAISE EXCEPTION '% assignee(s) are not members of the project', invalid_assignees;
    END IF;
    
    -- Перевірка 4: Чи немає дублікатів задачі в борді
    IF EXISTS(
        SELECT 1 FROM Task 
        WHERE BoardID = v_board_id 
          AND Title = v_task_title
          AND Status != 'Done'
    ) THEN
        RAISE EXCEPTION 'Task with title "%" already exists in this board', v_task_title;
    END IF;

    RAISE NOTICE 'Validation passed. Creating task...';

    -- Створення основної задачі
    INSERT INTO Task (Title, Description, Status, Priority, DueDate, BoardID)
    VALUES (
        v_task_title,
        'Інтегруйте систему обробки платежів зі Stripe та LiqPay. Включіть обробку вебхуків, логіку повернення коштів та історію платежів.',
        'To Do',
        'High',
        CURRENT_DATE + INTERVAL '21 days',
        v_board_id
    )
    RETURNING TaskID INTO v_main_task_id;

    RAISE NOTICE 'Created main task with ID: %', v_main_task_id;

    -- Створення пов'язаних підзадач
    INSERT INTO Task (Title, Description, Status, Priority, DueDate, BoardID)
    VALUES (
        'Налаштування інтеграції Stripe API',
        'Налаштування облікових даних Stripe SDK та API',
        'To Do',
        'High',
        CURRENT_DATE + INTERVAL '5 days',
        v_board_id
    )
    RETURNING TaskID INTO v_subtask1_id;
    
    INSERT INTO Task (Title, Description, Status, Priority, DueDate, BoardID)
    VALUES (
        'Реалізація обробників вебхуків платежів',
        'Обробка успішних, невдалих платежів та вебхуків для повернення коштів',
        'To Do',
        'High',
        CURRENT_DATE + INTERVAL '10 days',
        v_board_id
    )
    RETURNING TaskID INTO v_subtask2_id;
    
    INSERT INTO Task (Title, Description, Status, Priority, DueDate, BoardID)
    VALUES (
        'Створення інтерфейсу користувача історії платежів',
        'Створити користувацький інтерфейс для перегляду платіжних транзакцій',
        'To Do',
        'Medium',
        CURRENT_DATE + INTERVAL '14 days',
        v_board_id
    )
    RETURNING TaskID INTO v_subtask3_id;
    
    INSERT INTO Task (Title, Description, Status, Priority, DueDate, BoardID)
    VALUES (
        'Напишіть тести інтеграції платежів',
        'Створення автоматизованих тестів для потоків платежів',
        'To Do',
        'Medium',
        CURRENT_DATE + INTERVAL '18 days',
        v_board_id
    )
    RETURNING TaskID INTO v_subtask4_id;

    RAISE NOTICE 'Created 4 subtasks: %, %, %, %', v_subtask1_id, v_subtask2_id, v_subtask3_id, v_subtask4_id;

    -- Отримання існуючих тегів
    SELECT TagID INTO v_backend_tag FROM Tag WHERE TagName = 'Backend' LIMIT 1;
    SELECT TagID INTO v_urgent_tag FROM Tag WHERE TagName = 'Urgent' LIMIT 1;

    -- Прив'язка тегів до основної задачі
    IF v_backend_tag IS NOT NULL THEN
        INSERT INTO Task_Tag (TaskID, TagID)
        VALUES (v_main_task_id, v_backend_tag)
        ON CONFLICT (TaskID, TagID) DO NOTHING;
    END IF;

    IF v_urgent_tag IS NOT NULL THEN
        INSERT INTO Task_Tag (TaskID, TagID)
        VALUES (v_main_task_id, v_urgent_tag)
        ON CONFLICT (TaskID, TagID) DO NOTHING;
    END IF;

    -- Прив'язка тегів до підзадач 
    IF v_backend_tag IS NOT NULL THEN
        INSERT INTO Task_Tag (TaskID, TagID)
        VALUES 
            (v_subtask1_id, v_backend_tag),
            (v_subtask2_id, v_backend_tag)
        ON CONFLICT (TaskID, TagID) DO NOTHING;
    END IF;

    -- Призначення виконавців до основної задачі
    FOREACH i IN ARRAY v_assignee_ids
    LOOP
        INSERT INTO Task_Assignee (TaskID, UserID)
        VALUES (v_main_task_id, i)
        ON CONFLICT (TaskID, UserID) DO NOTHING;
    END LOOP;

    -- Розподіл підзадач між виконавцями
    INSERT INTO Task_Assignee (TaskID, UserID)
    VALUES 
        (v_subtask1_id, 2), 
        (v_subtask2_id, 2), 
        (v_subtask3_id, 4), 
        (v_subtask4_id, 2) 
    ON CONFLICT (TaskID, UserID) DO NOTHING;

    -- Створення початкових коментарів
    INSERT INTO Comment (Content, UserID, TaskID)
    VALUES (
        'Інтеграція платежів є критично важливою для запуску. Пріоритет: спочатку Stripe, потім LiqPay для локального ринку. Потрібно обробляти крайні випадки збоїв мережі.',
        1,  
        v_main_task_id
    );

    INSERT INTO Comment (Content, UserID, TaskID)
    VALUES (
        'Починаємо з налаштування Stripe SDK. Створимо обліковий запис sandbox для тестування..',
        2, 
        v_subtask1_id
    );


    RAISE NOTICE 'Main Task: % (ID: %)', v_task_title, v_main_task_id;
    RAISE NOTICE 'Subtasks created: 4';
    RAISE NOTICE 'Assignees: % users', array_length(v_assignee_ids, 1);
    RAISE NOTICE 'Tags applied: Backend, Urgent';
    RAISE NOTICE 'Comments added: 2';
    RAISE NOTICE 'Status: Successfully created';

EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Duplicate entry detected: %', SQLERRM;
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'Referenced entity does not exist: %', SQLERRM;
    WHEN check_violation THEN
        RAISE EXCEPTION 'Data validation failed: %', SQLERRM;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Task creation failed: %', SQLERRM;
END $$;


SELECT 
    t.TaskID,
    t.Title,
    t.Status,
    t.Priority,
    t.DueDate,
    b.BoardName,
    p.ProjectName,
    STRING_AGG(DISTINCT u.FullName, ', ') as Assignees,
    STRING_AGG(DISTINCT tg.TagName, ', ') as Tags
FROM Task t
JOIN Board b ON t.BoardID = b.BoardID
JOIN Project p ON b.ProjectID = p.ProjectID
LEFT JOIN Task_Assignee ta ON t.TaskID = ta.TaskID
LEFT JOIN "User" u ON ta.UserID = u.UserID
LEFT JOIN Task_Tag tt ON t.TaskID = tt.TaskID
LEFT JOIN Tag tg ON tt.TagID = tg.TagID
WHERE t.Title = 'Payment Integration System'
GROUP BY t.TaskID, b.BoardName, p.ProjectName;

-----------------------------------------------------------------------------------------------------------------
-- 2.1 Сценарій: Оновлення статусу задачі з валідацією та транзакційністю
BEGIN;

-- Перевірка поточного стану (песимістичне блокування)
SELECT Status, BoardID 
FROM Task 
WHERE TaskID = 1 
FOR UPDATE;

-- Валідація умов оновлення
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM Task 
        WHERE TaskID = 1 AND Status IN ('To Do', 'In Progress')
    ) THEN
        RAISE EXCEPTION 'Неможливо оновити: задача вже завершена або скасована';
    END IF;
END $$;

-- Оновлення статусу
UPDATE Task 
SET Status = 'In Progress'
WHERE TaskID = 1 
  AND Status = 'To Do';

-- Перевірка успішності оновлення
IF NOT FOUND THEN
    RAISE EXCEPTION 'Задача вже була оновлена іншим користувачем';
END IF;

COMMIT;

-----------------------------------------------------------------------------------------------------------------
-- 2.2 Масове оновлення дедлайнів задач з високим пріоритетом
BEGIN;

UPDATE Task 
SET DueDate = CURRENT_DATE + INTERVAL '3 days'
WHERE Priority = 'High' 
  AND Status IN ('To Do', 'In Progress')
  AND (DueDate IS NULL OR DueDate > CURRENT_DATE + INTERVAL '3 days');

-- Повернення оновлених рядків
SELECT TaskID, Title, DueDate, Priority
FROM Task
WHERE Priority = 'High' 
  AND DueDate = CURRENT_DATE + INTERVAL '3 days';

COMMIT;

-----------------------------------------------------------------------------------------------------------------
-- 3.1 Жорстоке видалення завершеного проєкту з усіма пов'язаними даними
BEGIN;

-- Перевірка перед видаленням
DO $$
DECLARE
    project_end DATE;
BEGIN
    SELECT EndDate INTO project_end 
    FROM Project 
    WHERE ProjectID = 3;
    
    IF project_end IS NULL THEN
        RAISE EXCEPTION 'Неможливо видалити активний проєкт';
    END IF;
    
    IF project_end > CURRENT_DATE - INTERVAL '30 days' THEN
        RAISE EXCEPTION 'Проєкт завершено менше 30 днів тому';
    END IF;
END $$;

DELETE FROM Project WHERE ProjectID = 3;

COMMIT;

-----------------------------------------------------------------------------------------------------------------
-- 3.2 Спочатку додати колонку (якщо немає)
ALTER TABLE "User" ADD COLUMN IF NOT EXISTS IsActive BOOLEAN DEFAULT TRUE;
ALTER TABLE "User" ADD COLUMN IF NOT EXISTS DeactivatedAt TIMESTAMP DEFAULT NULL;

BEGIN;

-- Перевірка перед деактивацією
DO $$
DECLARE
    active_tasks INT;
BEGIN
    SELECT COUNT(*) INTO active_tasks
    FROM Task_Assignee ta
    JOIN Task t ON ta.TaskID = t.TaskID
    WHERE ta.UserID = 5 
      AND t.Status IN ('To Do', 'In Progress');
    
    IF active_tasks > 0 THEN
        RAISE EXCEPTION 'Користувач має % активних задач. Переназначте їх перед деактивацією', active_tasks;
    END IF;
END $$;

-- М'яке видалення
UPDATE "User" 
SET IsActive = FALSE,
    DeactivatedAt = CURRENT_TIMESTAMP
WHERE UserID = 5 
  AND IsActive = TRUE;

COMMIT;

SELECT * FROM "User" WHERE IsActive = TRUE;

-----------------------------------------------------------------------------------------------------------------
-- 4.1.1 Вибрати всі проєкти з командами
SELECT p.ProjectID, p.ProjectName, t.TeamName
FROM Project p
LEFT JOIN Team t ON p.TeamID = t.TeamID;

-----------------------------------------------------------------------------------------------------------------
-- 4.1.2 Усі активні проєкти
SELECT * FROM Project WHERE EndDate IS NULL;

-----------------------------------------------------------------------------------------------------------------
-- 4.2.1 Останні коментарі з фільтрацією та пагінацією
SELECT 
    c.CommentID,
    c.Content,
    c.CreatedAt,
    u.FullName as Author,
    t.Title as TaskTitle,
    t.Status as TaskStatus
FROM Comment c
JOIN "User" u ON c.UserID = u.UserID
JOIN Task t ON c.TaskID = t.TaskID
WHERE c.CreatedAt > CURRENT_DATE - INTERVAL '30 days'
  AND t.Status != 'Done'
ORDER BY c.CreatedAt DESC
LIMIT 20 OFFSET 0;

-----------------------------------------------------------------------------------------------------------------
-- 4.2.2 Критичні задачі з найближчим дедлайном
SELECT 
    t.TaskID,
    t.Title,
    t.Priority,
    t.DueDate,
    t.Status,
    b.BoardName,
    EXTRACT(DAY FROM (t.DueDate - CURRENT_DATE)) as DaysRemaining
FROM Task t
JOIN Board b ON t.BoardID = b.BoardID
WHERE t.DueDate BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
  AND t.Status IN ('To Do', 'In Progress')
ORDER BY t.DueDate ASC, t.Priority DESC;

-----------------------------------------------------------------------------------------------------------------
-- 5.1 Задачі з повною інформацією
SELECT 
    t.TaskID, t.Title, b.BoardName, p.ProjectName,
    STRING_AGG(DISTINCT u.FullName, ', ') AS Assignees,
    STRING_AGG(DISTINCT tg.TagName, ', ') AS Tags
FROM Task t
JOIN Board b ON t.BoardID = b.BoardID
JOIN Project p ON b.ProjectID = p.ProjectID
LEFT JOIN Task_Assignee ta ON t.TaskID = ta.TaskID
LEFT JOIN "User" u ON ta.UserID = u.UserID
LEFT JOIN Task_Tag tt ON t.TaskID = tt.TaskID
LEFT JOIN Tag tg ON tt.TagID = tg.TagID
GROUP BY t.TaskID, b.BoardID, p.ProjectID;

-----------------------------------------------------------------------------------------------------------------
-- 5.2 Аналіз навантаження команд з деталізацією по проєктах
WITH TeamProjects AS (
    SELECT 
        t.TeamID,
        t.TeamName,
        COUNT(DISTINCT p.ProjectID) as ActiveProjects,
        COUNT(DISTINCT b.BoardID) as TotalBoards,
        COUNT(DISTINCT task.TaskID) as TotalTasks,
        COUNT(DISTINCT CASE WHEN task.Status != 'Done' THEN task.TaskID END) as PendingTasks,
        STRING_AGG(DISTINCT p.ProjectName, ', ' ORDER BY p.ProjectName) as ProjectList
    FROM Team t
    LEFT JOIN Project p ON t.TeamID = p.TeamID AND p.EndDate IS NULL
    LEFT JOIN Board b ON p.ProjectID = b.ProjectID
    LEFT JOIN Task task ON b.BoardID = task.BoardID
    GROUP BY t.TeamID, t.TeamName
)
SELECT *,
    ROUND(100.0 * PendingTasks / NULLIF(TotalTasks, 0), 2) as TaskCompletionRate,
    CASE 
        WHEN ActiveProjects >= 3 THEN 'Overloaded'
        WHEN ActiveProjects = 2 THEN 'Busy'
        WHEN ActiveProjects = 1 THEN 'Normal'
        ELSE 'Idle'
    END as WorkloadStatus
FROM TeamProjects
ORDER BY ActiveProjects DESC, PendingTasks DESC;