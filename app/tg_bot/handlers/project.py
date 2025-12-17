from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.company.services import company_service
from app.employee.services import employee_service
from app.project.services import project_service
from app.core.exceptions import ApplicationError
from app.tg_bot.states.project import ProjectCreation
from app.tg_bot.utils.callback_data import CompanyCallback, ProjectCallback
from app.tg_bot.utils.formatters import format_project_details
from app.tg_bot.utils.pagination import get_pagination_params, calculate_total_pages
from app.tg_bot.utils.error_handlers import handle_service_error
from app.tg_bot.keyboards.inline import (
    build_list_keyboard,
    build_project_details_keyboard,
    build_confirm_keyboard,
)


async def cmd_new_project(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await company_service.get_my_companies(user_tg_id, pagination)

    if not page_data.data:
        await message.answer("You don't have any companies. Use /new_company to create one first.")
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Select Company for New Project</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{c.code} - {c.name}", CompanyCallback(action="select_for_project", company_id=c.id))
        for c in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=CompanyCallback
    )

    await state.set_state(ProjectCreation.waiting_for_company)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def callback_select_company_for_project(callback: CallbackQuery, callback_data: CompanyCallback, state: FSMContext):
    company_id = callback_data.company_id

    await state.update_data(company_id=company_id)
    await state.set_state(ProjectCreation.waiting_for_name)
    await callback.message.edit_text("Enter project name:")
    await callback.answer()


async def process_project_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ProjectCreation.waiting_for_code)
    await message.answer("Enter 3-letter project code:")


async def process_project_code(message: Message, state: FSMContext):
    code = message.text
    data = await state.get_data()
    user_tg_id = message.from_user.id

    try:
        project = await project_service.create_project(
            company_id=data['company_id'],
            name=data['name'],
            code=code,
            user_tg_id=user_tg_id
        )
        await message.answer(
            f"✅ Project created successfully!\n\n{format_project_details(project)}",
            parse_mode="HTML"
        )
        await state.clear()
    except ApplicationError as e:
        await handle_service_error(e, message)
        await state.clear()


async def cmd_projects(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await company_service.get_my_companies(user_tg_id, pagination)

    if not page_data.data:
        await message.answer("You don't have any companies. Use /new_company to create one first.")
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Select Company to View Projects</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{c.code} - {c.name}", CompanyCallback(action="view_projects", company_id=c.id))
        for c in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=CompanyCallback
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def callback_view_projects(callback: CallbackQuery, callback_data: CompanyCallback):
    company_id = callback_data.company_id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await project_service.get_projects(company_id, pagination)

    if not page_data.data:
        await callback.message.edit_text("This company has no projects yet. Use /new_project to create one.")
        await callback.answer()
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Projects</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{p.code} - {p.name}", ProjectCallback(action="details", project_id=p.id, company_id=company_id))
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


async def callback_project_page(callback: CallbackQuery, callback_data: ProjectCallback):
    company_id = callback_data.company_id
    page = callback_data.page

    pagination = get_pagination_params(page, page_size=5)
    page_data = await project_service.get_projects(company_id, pagination)

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Projects</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{p.code} - {p.name}", ProjectCallback(action="details", project_id=p.id, company_id=company_id))
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


async def callback_project_details(callback: CallbackQuery, callback_data: ProjectCallback):
    project_id = callback_data.project_id
    user_tg_id = callback.from_user.id

    try:
        project = await project_service.get_project_details(project_id)
        is_owner_or_admin = await employee_service.verify_user_is_owner_or_admin(project.company_id, user_tg_id)

        text = format_project_details(project)
        keyboard = build_project_details_keyboard(project_id, project.company_id, is_owner_or_admin)

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_project_delete(callback: CallbackQuery, callback_data: ProjectCallback):
    project_id = callback_data.project_id
    company_id = callback_data.company_id

    try:
        project = await project_service.get_project_details(project_id)

        confirm_callback = ProjectCallback(action="confirm_delete", project_id=project_id, company_id=company_id)
        cancel_callback = ProjectCallback(action="details", project_id=project_id, company_id=company_id)

        keyboard = build_confirm_keyboard(confirm_callback, cancel_callback)

        await callback.message.edit_text(
            f"⚠️ Are you sure you want to delete project <b>'{project.name}'</b>?\n\n"
            f"This action cannot be undone.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_project_confirm_delete(callback: CallbackQuery, callback_data: ProjectCallback):
    project_id = callback_data.project_id
    user_tg_id = callback.from_user.id

    try:
        await project_service.delete_project(project_id, user_tg_id)
        await callback.message.edit_text("✅ Project deleted successfully!")
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_project_back_to_list(callback: CallbackQuery, callback_data: ProjectCallback):
    company_id = callback_data.company_id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await project_service.get_projects(company_id, pagination)

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Projects</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{p.code} - {p.name}", ProjectCallback(action="details", project_id=p.id, company_id=company_id))
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


def register_project_handlers(router: Router):
    router.message.register(cmd_new_project, Command("new_project"))
    router.message.register(cmd_projects, Command("projects"))

    router.callback_query.register(
        callback_select_company_for_project,
        CompanyCallback.filter(F.action == "select_for_project")
    )
    router.callback_query.register(
        callback_view_projects,
        CompanyCallback.filter(F.action == "view_projects")
    )

    router.message.register(process_project_name, ProjectCreation.waiting_for_name)
    router.message.register(process_project_code, ProjectCreation.waiting_for_code)

    router.callback_query.register(
        callback_project_page,
        ProjectCallback.filter(F.action == "page")
    )
    router.callback_query.register(
        callback_project_details,
        ProjectCallback.filter(F.action == "details")
    )
    router.callback_query.register(
        callback_project_delete,
        ProjectCallback.filter(F.action == "delete")
    )
    router.callback_query.register(
        callback_project_confirm_delete,
        ProjectCallback.filter(F.action == "confirm_delete")
    )
    router.callback_query.register(
        callback_project_back_to_list,
        ProjectCallback.filter(F.action == "back_to_list")
    )
