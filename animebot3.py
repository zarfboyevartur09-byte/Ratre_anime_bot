import logging
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, html, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command

# 1. SOZLAMALAR (Token, Admin ID va Kanallar ro'yxati)
BOT_TOKEN = "8204645008:AAHgvL8UEkvk6EbkBXhqB0R5mYFTf-BBEvQ"
ADMIN_ID = 6205517419  # O'zingizning Telegram ID raqamingiz

# Majburiy tekshiriladigan kanallar ID raqamlari yoki username'lari
# DIQQAT: Bot bu kanallarda muloqotni tekshira olishi uchun albatta ADMIN bo'lishi shart!
KANALLAR = [
    "@uzbekcha_animelar8",  # 1-kanal username
    "-1001234567890",
]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 2. MA'LUMOTLAR BAZASI
def init_db():
    conn = sqlite3.connect("anime_base.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS animelar (
            kod TEXT PRIMARY KEY,
            nomi TEXT,
            file_id TEXT
        )
    """)
    conn.commit()
    conn.close()

# 3. KANALLARGA OBUNANI TEKSHIRISH FUNKSIYASI
async def check_subscription(user_id: int) -> bool:
    for kanal in KANALLAR:
        try:
            member = await bot.get_chat_member(chat_id=kanal, user_id=user_id)
            # Agar foydalanuvchi guruh/kanal tarkibida bo'lmasa yoki haydalgan bo'lsa
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            logging.error(f"Kanalni tekshirishda xatolik ({kanal}): {e}")
            # Agar kanal topilmasa yoki bot admin bo'lmasa, vaqtincha True qaytarib yuboradi
            continue
    return True

# 4. MAJBURIY OBUNA INTERFEYSI (Siz yuborgan rasmda ko'ringan tugmalar)
def get_subscribe_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 - kanal ↗️", url="https://t.me/uzbekcha_animelar8")],
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
    ])
    return keyboard

# Asosiy menyu inline tugmalari
def get_inline_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍿 Ko‘proq Animelar", callback_data="more_anime")],
        [InlineKeyboardButton(text="⭐ Saqlangan Animelar", callback_data="saved_anime")]
    ])

# Pastki menyu reply tugmalari
def get_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔄 Random Animelar"), KeyboardButton(text="🏆 Top Animelar")],
            [KeyboardButton(text="🎬 Oxirgi yuklanganlar"), KeyboardButton(text="☎️ Qo‘llab quvvatlash")],
            [KeyboardButton(text="💎 Premium"), KeyboardButton(text="👨‍💻 Dasturchi")]
        ],
        resize_keyboard=True
    )

# 5. /start KOMANDASI
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    user_id = message.from_user.id
    
    # Kanallarga a'zolikni tekshiramiz
    is_subscribed = await check_subscription(user_id)
    
    if not is_subscribed:
        await message.answer(
            text="Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling yoki zayavka yuboring ❗️",
            reply_markup=get_subscribe_keyboard()
        )
        return

    # Agar a'zo bo'lgan bo'lsa, start xabari chiqadi
    start_text = f"👋 <b>Salom</b> {html.bold(message.from_user.first_name)}\n\n🍿 <i>Animelar nomi yoki kodini kiriting:</i>"
    await message.answer(text=start_text, reply_markup=get_reply_keyboard(), parse_mode="HTML")
    await message.answer("Qo'shimcha bo'limlar:", reply_markup=get_inline_keyboard())

# 6. "✅ TEKSHIRISH" TUGMASI BOSILGANDA ISHLAYDIGAN HANDLER
@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(call: CallbackQuery):
    user_id = call.from_user.id
    is_subscribed = await check_subscription(user_id)
    
    if is_subscribed:
        # Eski xabarni o'chirib yuboramiz
        await call.message.delete()
        # Boshlang'ich xabarni ochamiz
        start_text = f"👋 <b>Salom</b> {html.bold(call.from_user.first_name)}\n\n🍿 <i>Animelar nomi yoki kodini kiriting:</i>"
        await call.message.answer(text=start_text, reply_markup=get_reply_keyboard(), parse_mode="HTML")
    else:
        # Agar hali ham hamma kanallarga a'zo bo'lmagan bo'lsa, ogohlantirish beramiz
        await call.answer("❌ Siz hali barcha kanallarga a'zo bo'lmadingiz!", show_alert=True)
        # 7. PASTKI TUGMALAR BOSILGANDA ISHLAYDIGAN HANDLERLAR
@dp.message(F.text == "🔄 Random Animelar")
@dp.message(Command("rand"))
async def rand_command(message: Message):
    await message.answer("🔄 Tasodifiy anime qidirilmoqda...")

@dp.message(F.text == "🏆 Top Animelar")
@dp.message(Command("top"))
async def top_command(message: Message):
    await message.answer("🏆 Eng ommabop animelar ro'yxati...")

@dp.message(F.text == "🎬 Oxirgi yuklanganlar")
@dp.message(Command("last"))
async def last_command(message: Message):
    await message.answer("🎬 Oxirgi yuklangan animelar ro'yxati...")

@dp.message(F.text == "☎️ Qo‘llab quvvatlash")
@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer("☎️ Qo‘llab-quvvatlash bo'limi: @zarfboyevvv ga murojaat qiling.")

@dp.message(F.text == "💎 Premium")
@dp.message(Command("premium"))
async def premium_command(message: Message):
    await message.answer("💎 Premium tariflar tez kunda qo'shiladi!")

@dp.message(F.text == "👨‍💻 Dasturchi")
@dp.message(Command("dev"))
async def dev_command(message: Message):
    await message.answer("👨‍💻 Bot dasturchisi: @zarfboyevvv")

# 8. KOMANDALAR HANDLERLARI
@dp.message(F.text == "🔄 Random Animelar")
@dp.message(Command("rand"))
async def rand_command(message: Message):
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Avval kanallarga a'zo bo'ling!", reply_markup=get_subscribe_keyboard())
        return
    await message.answer("🔄 Tasodifiy anime qidirilmoqda...")

# Qolgan barcha bo'limlarni ham shunday tekshirish xavfsizligi
@dp.message(F.text == "🏆 Top Animelar")
@dp.message(Command("top"))
async def top_command(message: Message):
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Avval kanallarga a'zo bo'ling!", reply_markup=get_subscribe_keyboard())
        return
    await message.answer("🏆 Eng ommabop animelar ro'yxati...")

# 9. ADMIN UCHUN: ANIME QO'SHISH (Bunga tekshiruv shart emas)
@dp.message(F.video, F.from_user.id == ADMIN_ID)
async def add_anime_video(message: Message):
    if not message.caption:
        await message.answer("❌ Iltimos, videoga izohda kod va nomni yozing!\n\nFormat: <code>kod | Anime Nomi</code>")
        return
    try:
        if "|" not in message.caption:
            await message.answer("❌ Xato format! O'rtasiga ( | ) qo'ying.")
            return
        kod, nomi = message.caption.split("|", 1)
        kod, nomi = kod.strip(), nomi.strip()
        file_id = message.video.file_id

        conn = sqlite3.connect("anime_base.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO animelar (kod, nomi, file_id) VALUES (?, ?, ?)", (kod, nomi, file_id))
        conn.commit()
        conn.close()
        await message.answer(f"✅ Anime qo'shildi!\n🔑 Kod: {kod}\n🎬 Nomi: {nomi}")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

# 10. FOYDALANUVCHILAR UCHUN: KOD ORQALI ANIME QIDIRISH
@dp.message(F.text)
async def search_anime(message: Message):
    # Foydalanuvchi kod kiritganda ham majburiy a'zolikni tekshiramiz
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling!", reply_markup=get_subscribe_keyboard())
        return

    user_code = message.text.strip()
    conn = sqlite3.connect("anime_base.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nomi, file_id FROM animelar WHERE kod = ?", (user_code,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        nomi, file_id = result
        await message.reply_video(video=file_id, caption=f"🎬 <b>{nomi}</b>\n\nMurojaat uchun: @zarfboyevvv")
    else:
        await message.answer("😔 Kechirasiz, bu kod bilan hech qanday anime topilmadi.")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")
