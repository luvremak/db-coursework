
## Запит 1: Аналіз витрат по проєктах (Project Stats)

**Бізнес-питання:** Скільки часу та грошей витрачено на кожен проєкт компанії? Необхідно згрупувати дані по проєктах, підсумувати час та розрахувати вартість робіт на основі погодинної ставки співробітників.

```sql
SELECT 
    project.code AS project_code, 
    SUM(time_tracking_entry.duration_minutes) AS total_minutes, 
    SUM(
        (time_tracking_entry.duration_minutes / CAST(60.0 AS FLOAT)) * employee.salary_per_hour
    ) AS total_cost 
FROM time_tracking_entry 
JOIN employee ON time_tracking_entry.employee_id = employee.id 
JOIN task ON time_tracking_entry.task_id = task.id 
JOIN project ON task.project_id = project.id 
WHERE project.company_id = 2 
GROUP BY project.code 
ORDER BY total_cost DESC;
```

## Запит 2: Детальний звіт по ефективності співробітників (Employee Stats)

Бізнес-питання: Отримати детальний список усіх записів часу для конкретної компанії з інформацією про співробітника, задачу та вартість. Також потрібно бачити накопичувальний підсумок часу для кожного співробітника.

```sql
SELECT 
    project.code AS project_code, 
    task.code AS task_code, 
    task.name AS task_name, 
    employee.display_name AS employee_display_name, 
    time_tracking_entry.created_at, 
    time_tracking_entry.duration_minutes, 
    SUM(time_tracking_entry.duration_minutes) OVER (PARTITION BY employee.id) AS employee_total_minutes, 
    (time_tracking_entry.duration_minutes / CAST(60.0 AS FLOAT)) * employee.salary_per_hour AS salary_cost, 
    ROW_NUMBER() OVER (PARTITION BY employee.telegram_id ORDER BY time_tracking_entry.created_at DESC) AS entry_rank 
FROM time_tracking_entry 
JOIN employee ON time_tracking_entry.employee_id = employee.id 
JOIN task ON time_tracking_entry.task_id = task.id 
JOIN project ON task.project_id = project.id 
WHERE project.company_id = 2 
ORDER BY employee.display_name, time_tracking_entry.created_at DESC;
```
