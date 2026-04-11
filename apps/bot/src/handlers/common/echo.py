from aiogram import F, Router
from aiogram.types import Message

router = Router(name="echo")


@router.message(F.text)
async def echo_handler(message: Message) -> None:
    await message.answer(message.text)


@router.message()
async def unsupported_message_handler(message: Message) -> None:
    await message.answer("I can only echo text messages for now.")
