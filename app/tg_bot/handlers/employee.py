from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.company.services import company_service
from app.employee.services import employee_service
from app.core.exceptions import ApplicationError
from app.tg_bot.states.employee import EmployeeCreation, EmployeeModification
from app.tg_bot.utils.callback_data import CompanyCallback, EmployeeCallback
from app.tg_bot.utils.formatters import format_employee_details
from app.tg_bot.utils.pagination import get_pagination_params, calculate_total_pages
from app.tg_bot.utils.error_handlers import handle_service_error
from app.tg_bot.keyboards.inline import (
    build_list_keyboard,
    build_employee_details_keyboard,
)


async def cmd_new_employee(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await company_service.get_my_companies(user_tg_id, pagination)

    if not page_data.data:
        await message.answer("You don't have any companies. Use /new_company to create one first.")
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Select Company for New Employee</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{c.code} - {c.name}", CompanyCallback(action="select_for_employee", company_id=c.id))
        for c in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=CompanyCallback
    )

    await state.set_state(EmployeeCreation.waiting_for_company)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def callback_select_company_for_employee(callback: CallbackQuery, callback_data: CompanyCallback, state: FSMContext):
    company_id = callback_data.company_id

    await state.update_data(company_id=company_id)
    await state.set_state(EmployeeCreation.waiting_for_telegram_id)
    await callback.message.edit_text(
        "Send employee's Telegram contact in one of these ways:\n\n"
        "• Forward a message from them\n"
        "• Share their contact\n"
        "• Send their numeric Telegram ID"
    )
    await callback.answer()


async def process_employee_telegram_id(message: Message, state: FSMContext):
    telegram_id = None

    if message.contact:
        telegram_id = message.contact.user_id
        if message.contact.first_name:
            default_name = message.contact.first_name
            if message.contact.last_name:
                default_name += f" {message.contact.last_name}"
            await state.update_data(suggested_name=default_name)

    elif message.forward_date:
        if message.forward_from:
            telegram_id = message.forward_from.id
            if message.forward_from.first_name:
                default_name = message.forward_from.first_name
                if message.forward_from.last_name:
                    default_name += f" {message.forward_from.last_name}"
                await state.update_data(suggested_name=default_name)
        else:
            await message.answer(
                "❌ Cannot get Telegram ID from this forwarded message.\n"
                "The user's privacy settings prevent sharing their information.\n\n"
                "Please try another method:\n"
                "• Share their contact\n"
                "• Send their numeric Telegram ID"
            )
            return

    elif message.text:
        try:
            telegram_id = int(message.text.strip())
        except ValueError:
            await message.answer(
                "❌ Invalid input. Please use one of these methods:\n\n"
                "• Forward a message from the employee\n"
                "• Share their contact\n"
                "• Send their numeric Telegram ID"
            )
            return

    if telegram_id:
        await state.update_data(telegram_id=telegram_id)
        await state.set_state(EmployeeCreation.waiting_for_display_name)

        data = await state.get_data()
        if 'suggested_name' in data:
            await message.answer(f"Enter employee's display name (suggested: {data['suggested_name']}):")
        else:
            await message.answer("Enter employee's display name:")
    else:
        await message.answer(
            "❌ Could not extract Telegram ID. Please try again:\n\n"
            "• Forward a message from the employee\n"
            "• Share their contact\n"
            "• Send their numeric Telegram ID"
        )


async def process_employee_display_name(message: Message, state: FSMContext):
    await state.update_data(display_name=message.text)
    await state.set_state(EmployeeCreation.waiting_for_salary)
    await message.answer("Enter salary per hour (e.g., 25.50):")


async def process_employee_salary(message: Message, state: FSMContext):
    try:
        salary = float(message.text)
        if salary < 0:
            await message.answer("❌ Salary must be a positive number. Please try again:")
            return

        await state.update_data(salary_per_hour=salary)
        await state.set_state(EmployeeCreation.waiting_for_admin_status)
        await message.answer("Should this employee be an admin? (yes/no):")
    except ValueError:
        await message.answer("❌ Invalid salary. Please enter a valid number (e.g., 25.50):")


async def process_employee_admin_status(message: Message, state: FSMContext):
    text = message.text.lower()

    if text not in ['yes', 'no', 'y', 'n']:
        await message.answer("Please answer with 'yes' or 'no':")
        return

    is_admin = text in ['yes', 'y']
    data = await state.get_data()
    user_tg_id = message.from_user.id

    try:
        employee = await employee_service.create_employee(
            company_id=data['company_id'],
            telegram_id=data['telegram_id'],
            display_name=data['display_name'],
            salary_per_hour=data['salary_per_hour'],
            is_admin=is_admin,
            user_tg_id=user_tg_id
        )
        await message.answer(
            f"✅ Employee created successfully!\n\n{format_employee_details(employee)}",
            parse_mode="HTML"
        )
        await state.clear()
    except ApplicationError as e:
        await handle_service_error(e, message)
        await state.clear()


async def cmd_employees(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await company_service.get_my_companies(user_tg_id, pagination)

    if not page_data.data:
        await message.answer("You don't have any companies. Use /new_company to create one first.")
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Select Company to View Employees</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{c.code} - {c.name}", CompanyCallback(action="view_employees", company_id=c.id))
        for c in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=CompanyCallback
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def callback_view_employees(callback: CallbackQuery, callback_data: CompanyCallback):
    company_id = callback_data.company_id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await employee_service.get_employees(company_id, pagination)

    if not page_data.data:
        await callback.message.edit_text("This company has no employees yet. Use /new_employee to add one.")
        await callback.answer()
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Employees</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{e.display_name} - {e.telegram_id}", EmployeeCallback(action="details", employee_id=e.id, company_id=company_id))
        for e in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=lambda action, page: EmployeeCallback(action=action, company_id=company_id, page=page)
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


async def callback_employee_page(callback: CallbackQuery, callback_data: EmployeeCallback):
    company_id = callback_data.company_id
    page = callback_data.page

    pagination = get_pagination_params(page, page_size=5)
    page_data = await employee_service.get_employees(company_id, pagination)

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Employees</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{e.display_name} - {e.telegram_id}", EmployeeCallback(action="details", employee_id=e.id, company_id=company_id))
        for e in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=lambda action, page: EmployeeCallback(action=action, company_id=company_id, page=page)
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


async def callback_employee_details(callback: CallbackQuery, callback_data: EmployeeCallback):
    employee_id = callback_data.employee_id
    user_tg_id = callback.from_user.id

    try:
        employee = await employee_service.get_employee_details(employee_id)
        is_admin = await employee_service.verify_user_is_owner_or_admin(employee.company_id, user_tg_id)

        text = format_employee_details(employee)
        keyboard = build_employee_details_keyboard(employee_id, employee.company_id, is_admin, employee.is_active)

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_set_display_name(callback: CallbackQuery, callback_data: EmployeeCallback, state: FSMContext):
    employee_id = callback_data.employee_id
    company_id = callback_data.company_id

    await state.update_data(employee_id=employee_id, company_id=company_id)
    await state.set_state(EmployeeModification.waiting_for_display_name)
    await callback.message.edit_text("Enter new display name:")
    await callback.answer()


async def process_new_display_name(message: Message, state: FSMContext):
    data = await state.get_data()
    employee_id = data['employee_id']
    company_id = data['company_id']
    user_tg_id = message.from_user.id

    try:
        employee = await employee_service.set_display_name(employee_id, message.text, user_tg_id)
        is_admin = await employee_service.verify_user_is_owner_or_admin(company_id, user_tg_id)

        text = f"✅ Display name updated!\n\n{format_employee_details(employee)}"
        keyboard = build_employee_details_keyboard(employee_id, company_id, is_admin, employee.is_active)

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await state.clear()
    except ApplicationError as e:
        await handle_service_error(e, message)
        await state.clear()


async def callback_set_salary(callback: CallbackQuery, callback_data: EmployeeCallback, state: FSMContext):
    employee_id = callback_data.employee_id
    company_id = callback_data.company_id

    await state.update_data(employee_id=employee_id, company_id=company_id)
    await state.set_state(EmployeeModification.waiting_for_salary)
    await callback.message.edit_text("Enter new salary per hour (e.g., 25.50):")
    await callback.answer()


async def process_new_salary(message: Message, state: FSMContext):
    data = await state.get_data()
    employee_id = data['employee_id']
    company_id = data['company_id']
    user_tg_id = message.from_user.id

    try:
        salary = float(message.text)
        if salary < 0:
            await message.answer("❌ Salary must be a positive number. Please try again:")
            return

        employee = await employee_service.set_salary_per_hour(employee_id, salary, user_tg_id)
        is_admin = await employee_service.verify_user_is_owner_or_admin(company_id, user_tg_id)

        text = f"✅ Salary updated!\n\n{format_employee_details(employee)}"
        keyboard = build_employee_details_keyboard(employee_id, company_id, is_admin, employee.is_active)

        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await state.clear()
    except ValueError:
        await message.answer("❌ Invalid salary. Please enter a valid number (e.g., 25.50):")
    except ApplicationError as e:
        await handle_service_error(e, message)
        await state.clear()


async def callback_toggle_active(callback: CallbackQuery, callback_data: EmployeeCallback):
    employee_id = callback_data.employee_id
    company_id = callback_data.company_id
    user_tg_id = callback.from_user.id

    try:
        employee = await employee_service.get_employee_details(employee_id)
        new_status = not employee.is_active

        employee = await employee_service.set_is_active(employee_id, new_status, user_tg_id)
        is_admin = await employee_service.verify_user_is_owner_or_admin(company_id, user_tg_id)

        status_msg = "activated" if new_status else "deactivated"
        text = f"✅ Employee {status_msg}!\n\n{format_employee_details(employee)}"
        keyboard = build_employee_details_keyboard(employee_id, company_id, is_admin, employee.is_active)

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_employee_back_to_list(callback: CallbackQuery, callback_data: EmployeeCallback):
    company_id = callback_data.company_id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await employee_service.get_employees(company_id, pagination)

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Employees</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{e.display_name} - {e.telegram_id}", EmployeeCallback(action="details", employee_id=e.id, company_id=company_id))
        for e in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=lambda action, page: EmployeeCallback(action=action, company_id=company_id, page=page)
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


def register_employee_handlers(router: Router):
    router.message.register(cmd_new_employee, Command("new_employee"))
    router.message.register(cmd_employees, Command("employees"))

    router.callback_query.register(
        callback_select_company_for_employee,
        CompanyCallback.filter(F.action == "select_for_employee")
    )
    router.callback_query.register(
        callback_view_employees,
        CompanyCallback.filter(F.action == "view_employees")
    )

    router.message.register(process_employee_telegram_id, EmployeeCreation.waiting_for_telegram_id)
    router.message.register(process_employee_display_name, EmployeeCreation.waiting_for_display_name)
    router.message.register(process_employee_salary, EmployeeCreation.waiting_for_salary)
    router.message.register(process_employee_admin_status, EmployeeCreation.waiting_for_admin_status)

    router.message.register(process_new_display_name, EmployeeModification.waiting_for_display_name)
    router.message.register(process_new_salary, EmployeeModification.waiting_for_salary)

    router.callback_query.register(
        callback_employee_page,
        EmployeeCallback.filter(F.action == "page")
    )
    router.callback_query.register(
        callback_employee_details,
        EmployeeCallback.filter(F.action == "details")
    )
    router.callback_query.register(
        callback_set_display_name,
        EmployeeCallback.filter(F.action == "set_display_name")
    )
    router.callback_query.register(
        callback_set_salary,
        EmployeeCallback.filter(F.action == "set_salary")
    )
    router.callback_query.register(
        callback_toggle_active,
        EmployeeCallback.filter(F.action == "toggle_active")
    )
    router.callback_query.register(
        callback_employee_back_to_list,
        EmployeeCallback.filter(F.action == "back_to_list")
    )
