from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from sql import init_db, save_message, get_user_id_from_username

API_TOKEN = "BOT_TOKEN"  # Bot tokenini o'rnating
ADMINS = ['ADMIN_API']  # Adminlarning Telegram ID raqamlari

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# State yaratish
class Form(StatesGroup):
    awaiting_reply = State()  # Admin javobini kutish


# Start komandasi
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.reply("Salom, Admin! Sizga foydalanuvchilardan xabarlar keladi.")
    else:
         await message.reply(
                    "<b>Assalomu alaykum, xush kelibsiz!</b>\n\n"
                    "Men <i>Easy 8.0</i> kanalining yordamchi botiman.\n\n"
                    "Sizni qizitgan mavzu haqida xabar qoldiring, biz sizga albatta javob beramiz!",
                    parse_mode="HTML"
                )


# Foydalanuvchi xabarlari
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def user_message_handler(message: types.Message):
    # Adminlarga foydalanuvchi xabarini yuborish
    admin_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Javob berish", callback_data=f"reply:{message.from_user.id}")
    )
    for admin in ADMINS:
        await bot.send_message(
            admin,
            f"Yangi xabar:\n👤 Foydalanuvchi: @{message.from_user.username or 'Noma`lum'}\n📩 Xabar: {message.text}",
            reply_markup=admin_markup,
        )
    await message.reply("Xabaringiz adminga yuborildi, tez orada sizga javob beramiz!\nIltimos kuting.")


# Admin javobini qayta ishlash
@dp.callback_query_handler(lambda c: c.data.startswith("reply:"))
async def admin_reply_start(callback_query: types.CallbackQuery):
    # Callback ma'lumotlarini olish
    user_id = int(callback_query.data.split(":")[1])

    # Admin javob yozishi uchun ko'rsatma
    await bot.send_message(
        callback_query.from_user.id,
        f"Foydalanuvchi uchun javob yozing (ID: {user_id}):",
    )

    # Javob holatini saqlash va admin javobini kutish
    await Form.awaiting_reply.set()  # "awaiting_reply" holatini o'rnatish
    await dp.current_state().update_data(user_id=user_id)
    await callback_query.answer("Javobni yozing.")


@dp.message_handler(state=Form.awaiting_reply)
async def admin_send_reply(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")

    # Foydalanuvchiga admin javobini yuborish
    await bot.send_message(
        user_id,
        f"<b>📥 Admin javobi:</b>\n\n{message.text}",
        parse_mode="HTML"
    )

    # Adminni xabardor qilish
    await message.reply("Javob foydalanuvchiga yuborildi.")
    await state.finish()  # Holatni tugatish


# Botni ishga tushirish
if __name__ == "__main__":
    import asyncio


    async def main():
        await init_db()
        await dp.start_polling()


    asyncio.run(main())
