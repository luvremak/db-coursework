from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.company.services import company_service
from app.employee.services import employee_service
from app.project.services import project_service
from app.task.services import task_service
from app.time_tracking.services import time_tracking_entry_service
from app.core.exceptions import ApplicationError
from app.tg_bot.states.task import TaskCreation, TaskModification, TimeTracking
from app.tg_bot.utils.callback_data import CompanyCallback, ProjectCallback, TaskCallback, EmployeeCallback
from app.tg_bot.utils.formatters import format_task_details
from app.tg_bot.utils.pagination import get_pagination_params, calculate_total_pages
from app.tg_bot.utils.error_handlers import handle_service_error
from app.tg_bot.keyboards.inline import (
    build_list_keyboard,
    build_task_details_keyboard,
    build_confirm_keyboard,
    build_status_selection_keyboard,
)


def parse_flexible_deadline(date_string: str) -> datetime:
    date_string = date_string.strip()
    current_year = datetime.now().year

    formats = [
        ("%Y-%m-%d %H:%M", date_string),
        ("%m-%d %H:%M", f"{current_year}-{date_string}"),
        ("%Y-%m-%d", f"{date_string} 00:00"),
        ("%m-%d", f"{current_year}-{date_string} 00:00"),
    ]

    for fmt, processed_string in formats:
        try:
            return datetime.strptime(processed_string, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

    raise ValueError("Invalid date format")


async def get_tracked_minutes_for_user(task_id: int, company_id: int, user_tg_id: int) -> int:
    employee = await employee_service.get_employee_by_telegram_id_and_company_id(user_tg_id, company_id)
    if not employee:
        return 0
    return await time_tracking_entry_service.get_total_minutes_by_task_and_employee(task_id, employee.id)


async def cmd_new_task(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await company_service.get_my_companies(user_tg_id, pagination)

    if not page_data.data:
        await message.answer("You don't have any companies. Use /new_company to create one first.")
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Select Company for New Task</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{c.code} - {c.name}", CompanyCallback(action="select_for_task", company_id=c.id))
        for c in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=CompanyCallback
    )

    await state.set_state(TaskCreation.waiting_for_project)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def callback_select_company_for_task(callback: CallbackQuery, callback_data: CompanyCallback, state: FSMContext):
    company_id = callback_data.company_id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await project_service.get_projects(company_id, pagination)

    if not page_data.data:
        await callback.message.edit_text("This company has no projects yet. Use /new_project to create one first.")
        await callback.answer()
        await state.clear()
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Select Project for New Task</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{p.code} - {p.name}", ProjectCallback(action="select_for_task", project_id=p.id, company_id=company_id))
        for p in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=lambda action, page: ProjectCallback(action=action, company_id=company_id, page=page)
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


async def callback_select_project_for_task(callback: CallbackQuery, callback_data: ProjectCallback, state: FSMContext):
    project_id = callback_data.project_id

    await state.update_data(project_id=project_id)
    await state.set_state(TaskCreation.waiting_for_name)
    await callback.message.edit_text("Enter task name:")
    await callback.answer()


async def process_task_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(TaskCreation.waiting_for_description)
    await message.answer("Enter task description:")


async def process_task_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(TaskCreation.waiting_for_deadline)
    await message.answer(
        "Enter deadline:\n"
        "• YYYY-MM-DD HH:MM (full format)\n"
        "• MM-DD HH:MM (uses current year)\n"
        "• YYYY-MM-DD (time defaults to 00:00)\n"
        "• MM-DD (uses current year, time 00:00)"
    )


async def process_task_deadline(message: Message, state: FSMContext):
    try:
        deadline = parse_flexible_deadline(message.text)
        data = await state.get_data()
        project_id = data['project_id']

        project = await project_service.get_project_details(project_id)
        company_id = project.company_id

        page = 1
        pagination = get_pagination_params(page, page_size=5)
        page_data = await employee_service.get_employees(company_id, pagination)

        if not page_data.data:
            await message.answer("❌ This company has no employees. Add employees first using /new_employee")
            await state.clear()
            return

        await state.update_data(deadline=deadline)
        await state.set_state(TaskCreation.waiting_for_assignee)

        total_pages = calculate_total_pages(page_data.total, page_size=5)
        text = f"<b>Select Assignee</b> (Page {page}/{total_pages}):\n\n"

        items = [
            (f"{e.display_name} ({e.telegram_id})", EmployeeCallback(action="select_for_task_assignee", employee_id=e.id, company_id=company_id))
            for e in page_data.data
        ]

        keyboard = build_list_keyboard(
            items=items,
            current_page=page,
            total_pages=total_pages,
            callback_factory=lambda action, page: EmployeeCallback(action="page_for_task_assignee", company_id=company_id, page=page)
        )

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    except ValueError:
        await message.answer(
            "❌ Invalid date format. Examples:\n"
            "• 2025-12-31 23:59\n"
            "• 12-31 23:59\n"
            "• 2025-12-31\n"
            "• 12-31"
        )
    except ApplicationError as e:
        await handle_service_error(e, message)
        await state.clear()


async def callback_select_employee_for_task_assignee(callback: CallbackQuery, callback_data: EmployeeCallback, state: FSMContext):
    employee_id = callback_data.employee_id
    current_state = await state.get_state()
    data = await state.get_data()
    user_tg_id = callback.from_user.id

    try:
        employee = await employee_service.get_employee_details(employee_id)
        assignee_user_id = employee.telegram_id

        if current_state == TaskCreation.waiting_for_assignee:
            task = await task_service.create_task(
                project_id=data['project_id'],
                name=data['name'],
                description=data['description'],
                deadline=data['deadline'],
                assignee_user_id=assignee_user_id,
                user_tg_id=user_tg_id
            )
            await callback.message.edit_text(
                f"✅ Task created successfully!\n\n{format_task_details(task)}",
                parse_mode="HTML"
            )
            await state.clear()
        elif current_state == TaskModification.waiting_for_assignee:
            task_id = data['task_id']
            project_id = data['project_id']

            task = await task_service.assign_to_user(task_id, assignee_user_id, user_tg_id)
            project = await project_service.get_project_details(project_id)

            is_admin = await employee_service.verify_user_is_owner_or_admin(project.company_id, user_tg_id)
            is_assignee = task.assignee_user_id == user_tg_id

            tracked_minutes = await get_tracked_minutes_for_user(task_id, project.company_id, user_tg_id)
            text = f"✅ Task assigned successfully!\n\n{format_task_details(task, tracked_minutes)}"
            keyboard = build_task_details_keyboard(task_id, project_id, is_admin, is_assignee)

            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            await state.clear()

        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)
        await state.clear()


async def callback_employee_page_for_task_assignee(callback: CallbackQuery, callback_data: EmployeeCallback):
    company_id = callback_data.company_id
    page = callback_data.page

    pagination = get_pagination_params(page, page_size=5)
    page_data = await employee_service.get_employees(company_id, pagination)

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Select Assignee</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{e.display_name} ({e.telegram_id})", EmployeeCallback(action="select_for_task_assignee", employee_id=e.id, company_id=company_id))
        for e in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=lambda action, page: EmployeeCallback(action="page_for_task_assignee", company_id=company_id, page=page)
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


async def cmd_my_tasks(message: Message):
    user_tg_id = message.from_user.id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await task_service.get_my_tasks(user_tg_id, pagination)

    if not page_data.data:
        await message.answer("You don't have any tasks assigned to you yet.")
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>My Tasks</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"#{t.code} - {t.name}", TaskCallback(action="details", task_id=t.id, project_id=t.project_id))
        for t in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=lambda action, page: TaskCallback(action=action, page=page)
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def cmd_tasks(message: Message):
    user_tg_id = message.from_user.id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await company_service.get_my_companies(user_tg_id, pagination)

    if not page_data.data:
        await message.answer("You don't have any companies. Use /new_company to create one first.")
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Select Company to View Tasks</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{c.code} - {c.name}", CompanyCallback(action="view_tasks", company_id=c.id))
        for c in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=CompanyCallback
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def handle_task_id_shortcut(message: Message):
    text = message.text.strip()
    user_tg_id = message.from_user.id

    import re
    pattern = r'^([A-Za-z]{3})-([A-Za-z]{3})-(\d+)$'
    match = re.match(pattern, text)

    if not match:
        return

    company_code, project_code, task_code_str = match.groups()
    task_code = int(task_code_str)

    try:
        task = await task_service.get_task_by_full_code(company_code, project_code, task_code)
        project = await project_service.get_project_details(task.project_id)

        is_admin = await employee_service.verify_user_is_owner_or_admin(project.company_id, user_tg_id)
        is_assignee = task.assignee_user_id == user_tg_id

        tracked_minutes = await get_tracked_minutes_for_user(task.id, project.company_id, user_tg_id)

        text = format_task_details(task, tracked_minutes)
        keyboard = build_task_details_keyboard(task.id, task.project_id, is_admin, is_assignee)

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

    except ApplicationError as e:
        await handle_service_error(e, message)


async def callback_view_tasks(callback: CallbackQuery, callback_data: CompanyCallback):
    company_id = callback_data.company_id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await project_service.get_projects(company_id, pagination)

    if not page_data.data:
        await callback.message.edit_text("This company has no projects yet. Use /new_project to create one first.")
        await callback.answer()
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Select Project to View Tasks</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{p.code} - {p.name}", ProjectCallback(action="view_tasks", project_id=p.id, company_id=company_id))
        for p in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=lambda action, page: ProjectCallback(action=action, company_id=company_id, page=page)
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


async def callback_view_project_tasks(callback: CallbackQuery, callback_data: ProjectCallback):
    project_id = callback_data.project_id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await task_service.get_tasks(project_id, pagination)

    if not page_data.data:
        await callback.message.edit_text("This project has no tasks yet. Use /new_task to create one.")
        await callback.answer()
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Tasks</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"#{t.code} - {t.name}", TaskCallback(action="details", task_id=t.id, project_id=project_id))
        for t in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=lambda action, page: TaskCallback(action=action, project_id=project_id, page=page)
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


async def callback_task_page(callback: CallbackQuery, callback_data: TaskCallback):
    project_id = callback_data.project_id
    page = callback_data.page

    if project_id:
        pagination = get_pagination_params(page, page_size=5)
        page_data = await task_service.get_tasks(project_id, pagination)

        total_pages = calculate_total_pages(page_data.total, page_size=5)
        text = f"<b>Tasks</b> (Page {page}/{total_pages}):\n\n"

        items = [
            (f"#{t.code} - {t.name}", TaskCallback(action="details", task_id=t.id, project_id=project_id))
            for t in page_data.data
        ]

        keyboard = build_list_keyboard(
            items=items,
            current_page=page,
            total_pages=total_pages,
            callback_factory=lambda action, page: TaskCallback(action=action, project_id=project_id, page=page)
        )
    else:
        user_tg_id = callback.from_user.id
        pagination = get_pagination_params(page, page_size=5)
        page_data = await task_service.get_my_tasks(user_tg_id, pagination)

        total_pages = calculate_total_pages(page_data.total, page_size=5)
        text = f"<b>My Tasks</b> (Page {page}/{total_pages}):\n\n"

        items = [
            (f"#{t.code} - {t.name}", TaskCallback(action="details", task_id=t.id, project_id=t.project_id))
            for t in page_data.data
        ]

        keyboard = build_list_keyboard(
            items=items,
            current_page=page,
            total_pages=total_pages,
            callback_factory=lambda action, page: TaskCallback(action=action, page=page)
        )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


async def callback_task_details(callback: CallbackQuery, callback_data: TaskCallback):
    task_id = callback_data.task_id
    user_tg_id = callback.from_user.id

    try:
        task = await task_service.get_task_details(task_id)
        project = await project_service.get_project_details(task.project_id)

        is_admin = await employee_service.verify_user_is_owner_or_admin(project.company_id, user_tg_id)
        is_assignee = task.assignee_user_id == user_tg_id

        tracked_minutes = await get_tracked_minutes_for_user(task_id, project.company_id, user_tg_id)
        text = format_task_details(task, tracked_minutes)
        keyboard = build_task_details_keyboard(task_id, task.project_id, is_admin, is_assignee)

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_track_time(callback: CallbackQuery, callback_data: TaskCallback, state: FSMContext):
    task_id = callback_data.task_id
    project_id = callback_data.project_id

    await state.update_data(task_id=task_id, project_id=project_id)
    await state.set_state(TimeTracking.waiting_for_duration)
    await callback.message.edit_text("Enter time duration in minutes (e.g., 30, 60, 120):")
    await callback.answer()


async def process_time_duration(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data['task_id']
    project_id = data['project_id']
    user_tg_id = message.from_user.id

    try:
        duration_minutes = int(message.text.strip())
        if duration_minutes <= 0:
            await message.answer("❌ Duration must be a positive number. Please try again:")
            return

        task = await task_service.get_task_details(task_id)
        project = await project_service.get_project_details(project_id)

        employee = await employee_service.get_employee_by_telegram_id_and_company_id(
            user_tg_id, project.company_id
        )

        if not employee:
            await message.answer("❌ You are not an employee of this company.")
            await state.clear()
            return

        await time_tracking_entry_service.create_time_entry(
            task_id=task_id,
            employee_id=employee.id,
            duration_minutes=duration_minutes,
        )

        is_admin = await employee_service.verify_user_is_owner_or_admin(project.company_id, user_tg_id)
        is_assignee = task.assignee_user_id == user_tg_id

        tracked_minutes = await get_tracked_minutes_for_user(task_id, project.company_id, user_tg_id)
        text = f"✅ Tracked {duration_minutes} minutes for this task!\n\n{format_task_details(task, tracked_minutes)}"
        keyboard = build_task_details_keyboard(task_id, project_id, is_admin, is_assignee)

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await state.clear()
    except ValueError:
        await message.answer("❌ Invalid duration. Please enter a valid number of minutes:")
    except ApplicationError as e:
        await handle_service_error(e, message)
        await state.clear()


async def callback_edit_name(callback: CallbackQuery, callback_data: TaskCallback, state: FSMContext):
    task_id = callback_data.task_id
    project_id = callback_data.project_id

    await state.update_data(task_id=task_id, project_id=project_id)
    await state.set_state(TaskModification.waiting_for_name)
    await callback.message.edit_text("Enter new task name:")
    await callback.answer()


async def process_new_task_name(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data['task_id']
    project_id = data['project_id']
    user_tg_id = message.from_user.id

    try:
        task = await task_service.edit_name(task_id, message.text, user_tg_id)
        project = await project_service.get_project_details(project_id)

        is_admin = await employee_service.verify_user_is_owner_or_admin(project.company_id, user_tg_id)
        is_assignee = task.assignee_user_id == user_tg_id

        tracked_minutes = await get_tracked_minutes_for_user(task_id, project.company_id, user_tg_id)
        text = f"✅ Task name updated!\n\n{format_task_details(task, tracked_minutes)}"
        keyboard = build_task_details_keyboard(task_id, project_id, is_admin, is_assignee)

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await state.clear()
    except ApplicationError as e:
        await handle_service_error(e, message)
        await state.clear()


async def callback_edit_description(callback: CallbackQuery, callback_data: TaskCallback, state: FSMContext):
    task_id = callback_data.task_id
    project_id = callback_data.project_id

    await state.update_data(task_id=task_id, project_id=project_id)
    await state.set_state(TaskModification.waiting_for_description)
    await callback.message.edit_text("Enter new task description:")
    await callback.answer()


async def process_new_task_description(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data['task_id']
    project_id = data['project_id']
    user_tg_id = message.from_user.id

    try:
        task = await task_service.edit_description(task_id, message.text, user_tg_id)
        project = await project_service.get_project_details(project_id)

        is_admin = await employee_service.verify_user_is_owner_or_admin(project.company_id, user_tg_id)
        is_assignee = task.assignee_user_id == user_tg_id

        tracked_minutes = await get_tracked_minutes_for_user(task_id, project.company_id, user_tg_id)
        text = f"✅ Task description updated!\n\n{format_task_details(task, tracked_minutes)}"
        keyboard = build_task_details_keyboard(task_id, project_id, is_admin, is_assignee)

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await state.clear()
    except ApplicationError as e:
        await handle_service_error(e, message)
        await state.clear()


async def callback_set_deadline(callback: CallbackQuery, callback_data: TaskCallback, state: FSMContext):
    task_id = callback_data.task_id
    project_id = callback_data.project_id

    await state.update_data(task_id=task_id, project_id=project_id)
    await state.set_state(TaskModification.waiting_for_deadline)
    await callback.message.edit_text(
        "Enter new deadline:\n"
        "• YYYY-MM-DD HH:MM (full format)\n"
        "• MM-DD HH:MM (uses current year)\n"
        "• YYYY-MM-DD (time defaults to 00:00)\n"
        "• MM-DD (uses current year, time 00:00)"
    )
    await callback.answer()


async def process_new_task_deadline(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data['task_id']
    project_id = data['project_id']
    user_tg_id = message.from_user.id

    try:
        deadline = parse_flexible_deadline(message.text)
        task = await task_service.set_deadline(task_id, deadline, user_tg_id)
        project = await project_service.get_project_details(project_id)

        is_admin = await employee_service.verify_user_is_owner_or_admin(project.company_id, user_tg_id)
        is_assignee = task.assignee_user_id == user_tg_id

        tracked_minutes = await get_tracked_minutes_for_user(task_id, project.company_id, user_tg_id)
        text = f"✅ Task deadline updated!\n\n{format_task_details(task, tracked_minutes)}"
        keyboard = build_task_details_keyboard(task_id, project_id, is_admin, is_assignee)

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await state.clear()
    except ValueError:
        await message.answer(
            "❌ Invalid date format. Examples:\n"
            "• 2025-12-31 23:59\n"
            "• 12-31 23:59\n"
            "• 2025-12-31\n"
            "• 12-31"
        )
    except ApplicationError as e:
        await handle_service_error(e, message)
        await state.clear()


async def callback_assign(callback: CallbackQuery, callback_data: TaskCallback, state: FSMContext):
    task_id = callback_data.task_id
    project_id = callback_data.project_id

    try:
        project = await project_service.get_project_details(project_id)
        company_id = project.company_id

        page = 1
        pagination = get_pagination_params(page, page_size=5)
        page_data = await employee_service.get_employees(company_id, pagination)

        if not page_data.data:
            await callback.answer("❌ This company has no employees", show_alert=True)
            return

        await state.update_data(task_id=task_id, project_id=project_id)
        await state.set_state(TaskModification.waiting_for_assignee)

        total_pages = calculate_total_pages(page_data.total, page_size=5)
        text = f"<b>Select Assignee</b> (Page {page}/{total_pages}):\n\n"

        items = [
            (f"{e.display_name} ({e.telegram_id})", EmployeeCallback(action="select_for_task_assignee", employee_id=e.id, company_id=company_id))
            for e in page_data.data
        ]

        keyboard = build_list_keyboard(
            items=items,
            current_page=page,
            total_pages=total_pages,
            callback_factory=lambda action, page: EmployeeCallback(action="page_for_task_assignee", company_id=company_id, page=page)
        )

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_change_status(callback: CallbackQuery, callback_data: TaskCallback):
    task_id = callback_data.task_id
    project_id = callback_data.project_id

    keyboard = build_status_selection_keyboard(task_id, project_id)
    await callback.message.edit_text("Select new status:", reply_markup=keyboard)
    await callback.answer()


async def callback_set_status(callback: CallbackQuery, callback_data: TaskCallback):
    task_id = callback_data.task_id
    project_id = callback_data.project_id
    status = callback_data.status
    user_tg_id = callback.from_user.id

    try:
        task = await task_service.update_status(task_id, status, user_tg_id)
        project = await project_service.get_project_details(project_id)

        is_admin = await employee_service.verify_user_is_owner_or_admin(project.company_id, user_tg_id)
        is_assignee = task.assignee_user_id == user_tg_id

        tracked_minutes = await get_tracked_minutes_for_user(task_id, project.company_id, user_tg_id)
        text = f"✅ Status updated!\n\n{format_task_details(task, tracked_minutes)}"
        keyboard = build_task_details_keyboard(task_id, project_id, is_admin, is_assignee)

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_delete_task(callback: CallbackQuery, callback_data: TaskCallback):
    task_id = callback_data.task_id
    project_id = callback_data.project_id

    try:
        task = await task_service.get_task_details(task_id)

        text = f"Are you sure you want to delete this task?\n\n{format_task_details(task)}"
        keyboard = build_confirm_keyboard(
            confirm_callback=TaskCallback(action="confirm_delete", task_id=task_id, project_id=project_id),
            cancel_callback=TaskCallback(action="details", task_id=task_id, project_id=project_id)
        )

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_confirm_delete_task(callback: CallbackQuery, callback_data: TaskCallback):
    task_id = callback_data.task_id
    user_tg_id = callback.from_user.id

    try:
        await task_service.delete_task(task_id, user_tg_id)
        await callback.message.edit_text("✅ Task deleted successfully!")
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_task_back_to_list(callback: CallbackQuery, callback_data: TaskCallback):
    project_id = callback_data.project_id
    page = 1

    if project_id:
        pagination = get_pagination_params(page, page_size=5)
        page_data = await task_service.get_tasks(project_id, pagination)

        total_pages = calculate_total_pages(page_data.total, page_size=5)
        text = f"<b>Tasks</b> (Page {page}/{total_pages}):\n\n"

        items = [
            (f"#{t.code} - {t.name}", TaskCallback(action="details", task_id=t.id, project_id=project_id))
            for t in page_data.data
        ]

        keyboard = build_list_keyboard(
            items=items,
            current_page=page,
            total_pages=total_pages,
            callback_factory=lambda action, page: TaskCallback(action=action, project_id=project_id, page=page)
        )
    else:
        user_tg_id = callback.from_user.id
        pagination = get_pagination_params(page, page_size=5)
        page_data = await task_service.get_my_tasks(user_tg_id, pagination)

        total_pages = calculate_total_pages(page_data.total, page_size=5)
        text = f"<b>My Tasks</b> (Page {page}/{total_pages}):\n\n"

        items = [
            (f"#{t.code} - {t.name}", TaskCallback(action="details", task_id=t.id, project_id=t.project_id))
            for t in page_data.data
        ]

        keyboard = build_list_keyboard(
            items=items,
            current_page=page,
            total_pages=total_pages,
            callback_factory=lambda action, page: TaskCallback(action=action, page=page)
        )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


def register_task_handlers(router: Router):
    router.message.register(cmd_new_task, Command("new_task"))
    router.message.register(cmd_my_tasks, Command("my_tasks"))
    router.message.register(cmd_tasks, Command("tasks"))

    router.callback_query.register(
        callback_select_company_for_task,
        CompanyCallback.filter(F.action == "select_for_task")
    )
    router.callback_query.register(
        callback_view_tasks,
        CompanyCallback.filter(F.action == "view_tasks")
    )

    router.callback_query.register(
        callback_select_project_for_task,
        ProjectCallback.filter(F.action == "select_for_task")
    )
    router.callback_query.register(
        callback_view_project_tasks,
        ProjectCallback.filter(F.action == "view_tasks")
    )

    router.message.register(process_task_name, TaskCreation.waiting_for_name)
    router.message.register(process_task_description, TaskCreation.waiting_for_description)
    router.message.register(process_task_deadline, TaskCreation.waiting_for_deadline)

    router.message.register(process_new_task_name, TaskModification.waiting_for_name)
    router.message.register(process_new_task_description, TaskModification.waiting_for_description)
    router.message.register(process_new_task_deadline, TaskModification.waiting_for_deadline)

    router.message.register(process_time_duration, TimeTracking.waiting_for_duration)

    router.callback_query.register(
        callback_select_employee_for_task_assignee,
        EmployeeCallback.filter(F.action == "select_for_task_assignee")
    )
    router.callback_query.register(
        callback_employee_page_for_task_assignee,
        EmployeeCallback.filter(F.action == "page_for_task_assignee")
    )

    router.callback_query.register(
        callback_task_page,
        TaskCallback.filter(F.action == "page")
    )
    router.callback_query.register(
        callback_task_details,
        TaskCallback.filter(F.action == "details")
    )
    router.callback_query.register(
        callback_track_time,
        TaskCallback.filter(F.action == "track_time")
    )
    router.callback_query.register(
        callback_edit_name,
        TaskCallback.filter(F.action == "edit_name")
    )
    router.callback_query.register(
        callback_edit_description,
        TaskCallback.filter(F.action == "edit_description")
    )
    router.callback_query.register(
        callback_set_deadline,
        TaskCallback.filter(F.action == "set_deadline")
    )
    router.callback_query.register(
        callback_assign,
        TaskCallback.filter(F.action == "assign")
    )
    router.callback_query.register(
        callback_change_status,
        TaskCallback.filter(F.action == "change_status")
    )
    router.callback_query.register(
        callback_set_status,
        TaskCallback.filter(F.action == "set_status")
    )
    router.callback_query.register(
        callback_delete_task,
        TaskCallback.filter(F.action == "delete")
    )
    router.callback_query.register(
        callback_confirm_delete_task,
        TaskCallback.filter(F.action == "confirm_delete")
    )
    router.callback_query.register(
        callback_task_back_to_list,
        TaskCallback.filter(F.action == "back_to_list")
    )

    router.message.register(handle_task_id_shortcut, F.text)
