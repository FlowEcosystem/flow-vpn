from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Hello. This is Flow VPN bot.\n\n"
        "Send me any text message and I will echo it back."
    )
