from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.application.status import StatusService
from src.presentation.telegram.callbacks import ACTION_STATUS, MENU_STATUS
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.client import build_status_menu
from src.presentation.telegram.screens.client import build_status_text

router = Router(name="client_status")


@router.callback_query(F.data == MENU_STATUS)
@router.callback_query(F.data == ACTION_STATUS)
async def status_callback_handler(
    callback: CallbackQuery,
    status: FromDishka[StatusService],
    state: FSMContext,
) -> None:
    overview = await status.get_status()
    await state.clear()
    await safe_edit_message(
        callback,
        text=build_status_text(overview),
        reply_markup=build_status_menu(),
    )
    await callback.answer()
