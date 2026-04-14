# ruff: noqa: RUF001

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message


def extract_referral_code(message_text: str | None) -> str | None:
    if not message_text:
        return None

    _, _, payload = message_text.partition(" ")
    if not payload.startswith("ref_"):
        return None

    referral_code = payload.removeprefix("ref_").strip().lower()
    return referral_code or None


async def safe_edit_message(
    callback: CallbackQuery,
    *,
    text: str,
    reply_markup: InlineKeyboardMarkup,
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    try:
        if message.photo:
            await message.delete()
            await message.answer(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc):
            raise
