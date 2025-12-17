import csv
import io
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from app.company.services import company_service
from app.time_tracking.services import time_tracking_entry_service
from app.core.exceptions import ApplicationError
from app.tg_bot.states.company import CompanyCreation
from app.tg_bot.utils.callback_data import CompanyCallback
from app.tg_bot.utils.formatters import format_company_details
from app.tg_bot.utils.pagination import get_pagination_params, calculate_total_pages
from app.tg_bot.utils.error_handlers import handle_service_error
from app.tg_bot.keyboards.inline import (
    build_list_keyboard,
    build_company_details_keyboard,
    build_confirm_keyboard,
)


async def cmd_new_company(message: Message, state: FSMContext):
    await state.set_state(CompanyCreation.waiting_for_name)
    await message.answer("Enter company name:")


async def process_company_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CompanyCreation.waiting_for_code)
    await message.answer("Enter 3-letter company code:")


async def process_company_code(message: Message, state: FSMContext):
    code = message.text
    data = await state.get_data()
    user_tg_id = message.from_user.id

    try:
        company = await company_service.create_company(
            name=data['name'],
            code=code,
            owner_tg_id=user_tg_id
        )
        await message.answer(
            f"✅ Company created successfully!\n\n{format_company_details(company)}",
            parse_mode="HTML"
        )
        await state.clear()
    except ApplicationError as e:
        await handle_service_error(e, message)
        await state.clear()


async def cmd_my_companies(message: Message):
    user_tg_id = message.from_user.id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await company_service.get_my_companies(user_tg_id, pagination)

    if not page_data.data:
        await message.answer("You don't have any companies yet. Use /new_company to create one.")
        return

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Your Companies</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{c.code} - {c.name}", CompanyCallback(action="details", company_id=c.id))
        for c in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=CompanyCallback
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def callback_company_page(callback: CallbackQuery, callback_data: CompanyCallback):
    user_tg_id = callback.from_user.id
    page = callback_data.page

    pagination = get_pagination_params(page, page_size=5)
    page_data = await company_service.get_my_companies(user_tg_id, pagination)

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Your Companies</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{c.code} - {c.name}", CompanyCallback(action="details", company_id=c.id))
        for c in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=CompanyCallback
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


async def callback_company_details(callback: CallbackQuery, callback_data: CompanyCallback):
    company_id = callback_data.company_id
    user_tg_id = callback.from_user.id

    try:
        company = await company_service.get_company_details(company_id)
        is_owner = await company_service.verify_user_is_owner(company_id, user_tg_id)

        text = format_company_details(company)
        keyboard = build_company_details_keyboard(company_id, is_owner)

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_company_delete(callback: CallbackQuery, callback_data: CompanyCallback):
    company_id = callback_data.company_id

    try:
        company = await company_service.get_company_details(company_id)

        confirm_callback = CompanyCallback(action="confirm_delete", company_id=company_id)
        cancel_callback = CompanyCallback(action="details", company_id=company_id)

        keyboard = build_confirm_keyboard(confirm_callback, cancel_callback)

        await callback.message.edit_text(
            f"⚠️ Are you sure you want to delete company <b>'{company.name}'</b>?\n\n"
            f"This action cannot be undone.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_company_confirm_delete(callback: CallbackQuery, callback_data: CompanyCallback):
    company_id = callback_data.company_id
    user_tg_id = callback.from_user.id

    try:
        await company_service.delete_company(company_id, user_tg_id)
        await callback.message.edit_text("✅ Company deleted successfully!")
        await callback.answer()
    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_back_to_list(callback: CallbackQuery):
    user_tg_id = callback.from_user.id
    page = 1

    pagination = get_pagination_params(page, page_size=5)
    page_data = await company_service.get_my_companies(user_tg_id, pagination)

    total_pages = calculate_total_pages(page_data.total, page_size=5)
    text = f"<b>Your Companies</b> (Page {page}/{total_pages}):\n\n"

    items = [
        (f"{c.code} - {c.name}", CompanyCallback(action="details", company_id=c.id))
        for c in page_data.data
    ]

    keyboard = build_list_keyboard(
        items=items,
        current_page=page,
        total_pages=total_pages,
        callback_factory=CompanyCallback
    )

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


async def callback_export_project_stats(callback: CallbackQuery, callback_data: CompanyCallback):
    company_id = callback_data.company_id
    user_tg_id = callback.from_user.id

    try:
        is_owner = await company_service.verify_user_is_owner(company_id, user_tg_id)
        if not is_owner:
            await callback.answer("Only company owner can export statistics", show_alert=True)
            return

        company = await company_service.get_company_details(company_id)
        rows = await time_tracking_entry_service.get_project_stats_for_company(company_id)

        if not rows:
            await callback.answer("No time tracking data available for export", show_alert=True)
            return

        output = io.StringIO()
        fieldnames = ["company_code", "project_code", "total_hours_spent", "total_money_spent"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

        csv_bytes = output.getvalue().encode('utf-8')
        output.close()

        filename = f"{company.code}_project_stats.csv"
        document = BufferedInputFile(csv_bytes, filename=filename)

        await callback.message.answer_document(
            document=document,
            caption=f"📊 Project statistics for {company.name}"
        )
        await callback.answer("CSV file generated successfully!")

    except ApplicationError as e:
        await handle_service_error(e, callback)


async def callback_export_employee_stats(callback: CallbackQuery, callback_data: CompanyCallback):
    company_id = callback_data.company_id
    user_tg_id = callback.from_user.id

    try:
        is_owner = await company_service.verify_user_is_owner(company_id, user_tg_id)
        if not is_owner:
            await callback.answer("Only company owner can export statistics", show_alert=True)
            return

        company = await company_service.get_company_details(company_id)
        rows = await time_tracking_entry_service.get_employee_stats_for_company(company_id)

        if not rows:
            await callback.answer("No time tracking data available for export", show_alert=True)
            return

        output = io.StringIO()
        fieldnames = [
            "company_code", "project_code", "task_code", "task_name",
            "employee_display_name", "created_at", "duration_minutes", "salary"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

        csv_bytes = output.getvalue().encode('utf-8')
        output.close()

        filename = f"{company.code}_employee_stats.csv"
        document = BufferedInputFile(csv_bytes, filename=filename)

        await callback.message.answer_document(
            document=document,
            caption=f"📊 Employee statistics for {company.name}"
        )
        await callback.answer("CSV file generated successfully!")

    except ApplicationError as e:
        await handle_service_error(e, callback)


def register_company_handlers(router: Router):
    router.message.register(cmd_new_company, Command("new_company"))
    router.message.register(cmd_my_companies, Command("my_companies"))

    router.message.register(process_company_name, CompanyCreation.waiting_for_name)
    router.message.register(process_company_code, CompanyCreation.waiting_for_code)

    router.callback_query.register(
        callback_company_page,
        CompanyCallback.filter(F.action == "page")
    )
    router.callback_query.register(
        callback_company_details,
        CompanyCallback.filter(F.action == "details")
    )
    router.callback_query.register(
        callback_export_project_stats,
        CompanyCallback.filter(F.action == "export_project_stats")
    )
    router.callback_query.register(
        callback_export_employee_stats,
        CompanyCallback.filter(F.action == "export_employee_stats")
    )
    router.callback_query.register(
        callback_company_delete,
        CompanyCallback.filter(F.action == "delete")
    )
    router.callback_query.register(
        callback_company_confirm_delete,
        CompanyCallback.filter(F.action == "confirm_delete")
    )
    router.callback_query.register(
        callback_back_to_list,
        CompanyCallback.filter(F.action == "back_to_list")
    )
