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


def build_back_button(callback_data: CallbackData) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(
        text="◀️ Back",
        callback_data=callback_data.pack()
    )]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
