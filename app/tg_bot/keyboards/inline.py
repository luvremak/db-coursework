from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData


def build_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_factory: CallbackData
) -> InlineKeyboardMarkup:
    buttons = []

    if current_page > 1:
        prev_callback = callback_factory(action="page", page=current_page - 1)
        buttons.append(InlineKeyboardButton(text="◀️ Previous", callback_data=prev_callback.pack()))

    if current_page < total_pages:
        next_callback = callback_factory(action="page", page=current_page + 1)
        buttons.append(InlineKeyboardButton(text="Next ▶️", callback_data=next_callback.pack()))

    if buttons:
        return InlineKeyboardMarkup(inline_keyboard=[buttons])
    return InlineKeyboardMarkup(inline_keyboard=[])


def build_list_keyboard(
    items: list[tuple[str, CallbackData]],
    current_page: int,
    total_pages: int,
    callback_factory: CallbackData
) -> InlineKeyboardMarkup:
    buttons = []

    for item_text, callback_data in items:
        buttons.append([InlineKeyboardButton(
            text=item_text,
            callback_data=callback_data.pack()
        )])

    pagination_buttons = []
    if current_page > 1:
        prev_callback = callback_factory(action="page", page=current_page - 1)
        pagination_buttons.append(InlineKeyboardButton(text="◀️ Previous", callback_data=prev_callback.pack()))

    if current_page < total_pages:
        next_callback = callback_factory(action="page", page=current_page + 1)
        pagination_buttons.append(InlineKeyboardButton(text="Next ▶️", callback_data=next_callback.pack()))

    if pagination_buttons:
        buttons.append(pagination_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_company_details_keyboard(company_id: int, is_owner: bool) -> InlineKeyboardMarkup:
    from app.tg_bot.utils.callback_data import CompanyCallback

    buttons = []

    if is_owner:
        delete_callback = CompanyCallback(action="delete", company_id=company_id)
        buttons.append([InlineKeyboardButton(
            text="🗑 Delete Company",
            callback_data=delete_callback.pack()
        )])

    back_callback = CompanyCallback(action="back_to_list")
    buttons.append([InlineKeyboardButton(
        text="◀️ Back to List",
        callback_data=back_callback.pack()
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_project_details_keyboard(project_id: int, company_id: int, is_owner_or_admin: bool) -> InlineKeyboardMarkup:
    from app.tg_bot.utils.callback_data import ProjectCallback

    buttons = []

    if is_owner_or_admin:
        delete_callback = ProjectCallback(action="delete", project_id=project_id, company_id=company_id)
        buttons.append([InlineKeyboardButton(
            text="🗑 Delete Project",
            callback_data=delete_callback.pack()
        )])

    back_callback = ProjectCallback(action="back_to_list", company_id=company_id)
    buttons.append([InlineKeyboardButton(
        text="◀️ Back to List",
        callback_data=back_callback.pack()
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_employee_details_keyboard(
    employee_id: int,
    company_id: int,
    is_admin: bool,
    is_active: bool
) -> InlineKeyboardMarkup:
    from app.tg_bot.utils.callback_data import EmployeeCallback

    buttons = []

    if is_admin:
        buttons.append([InlineKeyboardButton(
            text="✏️ Set Display Name",
            callback_data=EmployeeCallback(action="set_display_name", employee_id=employee_id, company_id=company_id).pack()
        )])

        buttons.append([InlineKeyboardButton(
            text="💰 Set Salary/Hour",
            callback_data=EmployeeCallback(action="set_salary", employee_id=employee_id, company_id=company_id).pack()
        )])

        status_text = "🔴 Deactivate" if is_active else "🟢 Activate"
        buttons.append([InlineKeyboardButton(
            text=status_text,
            callback_data=EmployeeCallback(action="toggle_active", employee_id=employee_id, company_id=company_id).pack()
        )])

    back_callback = EmployeeCallback(action="back_to_list", company_id=company_id)
    buttons.append([InlineKeyboardButton(
        text="◀️ Back to List",
        callback_data=back_callback.pack()
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_confirm_keyboard(
    confirm_callback: CallbackData,
    cancel_callback: CallbackData
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="✅ Confirm", callback_data=confirm_callback.pack()),
            InlineKeyboardButton(text="❌ Cancel", callback_data=cancel_callback.pack())
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_task_details_keyboard(
    task_id: int,
    project_id: int,
    is_admin: bool,
    is_assignee: bool
) -> InlineKeyboardMarkup:
    from app.tg_bot.utils.callback_data import TaskCallback

    buttons = []

    if is_assignee:
        buttons.append([InlineKeyboardButton(
            text="⏱ Track Time",
            callback_data=TaskCallback(action="track_time", task_id=task_id, project_id=project_id).pack()
        )])

    if is_admin:
        buttons.append([InlineKeyboardButton(
            text="✏️ Edit Name",
            callback_data=TaskCallback(action="edit_name", task_id=task_id, project_id=project_id).pack()
        )])

        buttons.append([InlineKeyboardButton(
            text="📝 Edit Description",
            callback_data=TaskCallback(action="edit_description", task_id=task_id, project_id=project_id).pack()
        )])

        buttons.append([InlineKeyboardButton(
            text="📅 Set Deadline",
            callback_data=TaskCallback(action="set_deadline", task_id=task_id, project_id=project_id).pack()
        )])

        buttons.append([InlineKeyboardButton(
            text="👤 Assign",
            callback_data=TaskCallback(action="assign", task_id=task_id, project_id=project_id).pack()
        )])

        buttons.append([InlineKeyboardButton(
            text="🔄 Change Status",
            callback_data=TaskCallback(action="change_status", task_id=task_id, project_id=project_id).pack()
        )])

        buttons.append([InlineKeyboardButton(
            text="🗑 Delete Task",
            callback_data=TaskCallback(action="delete", task_id=task_id, project_id=project_id).pack()
        )])

    back_callback = TaskCallback(action="back_to_list", project_id=project_id)
    buttons.append([InlineKeyboardButton(
        text="◀️ Back to List",
        callback_data=back_callback.pack()
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_status_selection_keyboard(task_id: int, project_id: int) -> InlineKeyboardMarkup:
    from app.tg_bot.utils.callback_data import TaskCallback

    statuses = [
        ("🆕 New", "new"),
        ("⚙️ In Progress", "in_progress"),
        ("👀 Review", "review"),
        ("✅ Done", "done"),
        ("❌ Canceled", "canceled"),
    ]

    buttons = []
    for label, status_value in statuses:
        buttons.append([InlineKeyboardButton(
            text=label,
            callback_data=TaskCallback(action="set_status", task_id=task_id, project_id=project_id, status=status_value).pack()
        )])

    back_callback = TaskCallback(action="details", task_id=task_id, project_id=project_id)
    buttons.append([InlineKeyboardButton(
        text="◀️ Back",
        callback_data=back_callback.pack()
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_back_button(callback_data: CallbackData) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(
        text="◀️ Back",
        callback_data=callback_data.pack()
    )]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
