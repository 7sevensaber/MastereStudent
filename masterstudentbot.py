import sqlite3

conn = sqlite3.connect("orders.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    topic TEXT,
    pages TEXT,
    status TEXT
)
""")

conn.commit()
import telebot
from telebot import types
import sqlite3

conn = sqlite3.connect("orders.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    topic TEXT,
    pages TEXT,
    price INTEGER,
    status TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

#==============+++++++++++================

TOKEN = "8067198161:AAHLJ2x3BmB0CfY5jqw77_wYWh86h2MX39Y"
ADMIN_ID = 7869424741  # admin telegram ID
ADMIN_USERNAME = "@MasterStudent_uz"


bot = telebot.TeleBot(TOKEN)

user_state = {}
user_data = {}
pending_delivery = {}

# ================= START MENU =================

def send_main_menu(chat_id):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.add(
        "📄 Mustaqil ish",
        "📊 Taqdimot (Slayd)"
    )

    markup.add(
        "🧾 Boshqa buyurtma"
    )

    bot.send_message(
        chat_id,

        "👋 Assalomu alaykum! Hurmatli mijoz.😉\n\n"
        "🖥 MASTER STUDENT botiga xush kelibsiz.\n\n"
        "🕹 Kerakli bo'limni tanlang:",

        reply_markup=markup
    )
    
#=============================Admin panels (/orders)====================================
@bot.message_handler(commands=['orders'])
def orders(message):

    if message.chat.id != ADMIN_ID:
        return

    cursor.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 20")
    data = cursor.fetchall()

    text = "📦 BUYURTMALAR:\n\n"

    for o in data:
        text += (
            f"ID: {o[0]}\n"
            f"User: {o[1]}\n"
            f"Mavzu: {o[2]}\n"
            f"Varaq: {o[3]}\n"
            f"Status: {o[4]}\n"
            "------------------\n"
        )

    bot.send_message(ADMIN_ID, text)

# ================= START =================

@bot.message_handler(commands=['start'])
def start(message):

    send_main_menu(
        message.chat.id
    )

# ================= MENU =================

@bot.message_handler(
    func=lambda m: True,
    content_types=['text']
)
def menu_handler(message):

    chat_id = message.chat.id
    text = message.text

    # BOSH MENU
    if text == "🏠 Bosh menyu":

        user_state.pop(
            chat_id,
            None
        )

        send_main_menu(
            chat_id
        )

    # MUSTAQIL ISH
    elif text == "📄 Mustaqil ish":

        user_state[chat_id] = "topic_ish"

        bot.send_message(
            chat_id,
            "📄 Iltimos mavzuni yozing:"
        )

    # TAQDIMOT
    elif text == "📊 Taqdimot (Slayd)":

        user_state[chat_id] = "topic_slide"

        bot.send_message(
            chat_id,
            "📊 Slayd mavzusini yozing:"
        )

    # BOSHQA BUYURTMA
    elif text == "🧾 Boshqa buyurtma":

        bot.send_message(
            chat_id,
            f"☎️ Admin bilan bog'lanish:\n{ADMIN_USERNAME}\n"
        )

    # MAVZU
    elif chat_id in user_state and user_state[chat_id] in ["topic_ish","topic_slide"]:

        user_data[chat_id] = {}

        user_data[chat_id]["topic"] = text

        user_state[chat_id] = "pages"

        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True
        )

        markup.add("0-10📄","10-15📄")
        markup.add("20-25📄","30-40📄")
        markup.add("50-60📄")

        bot.send_message(
            chat_id,
            "📑 Necha varoq bo'lsin?",
            reply_markup=markup
        )

    # PAGE TANLASH
    elif chat_id in user_state and user_state[chat_id] == "pages":
        cursor.execute(
         "INSERT INTO orders (user_id, topic, pages, status) VALUES (?, ?, ?, ?)",
        (chat_id, user_data[chat_id]["topic"], text, "pending")
        )
        conn.commit()

        user_data[chat_id]["pages"] = text
        user_state[chat_id] = "payment"

        remove_keyboard = types.ReplyKeyboardRemove()
#
        price_map = {
         "📑0-10": 10000,
         "📑10-15": 15000,
         "📑20-25": 20000,
         "📑30-40": 30000,
         "📑50-60": 50000
}

        price = price_map.get(text, 0)

        cursor.execute(
         "INSERT INTO orders (user_id, topic, pages, price, status) VALUES (?, ?, ?, ?, ?)",
        (chat_id, user_data[chat_id]["topic"], text, price, "pending")
)

        conn.commit()
#
        bot.send_message(

            chat_id,

            "💰 NARXLAR:\n\n"

            "📑0-10 → 10 000 so'm💵\n"
            "📑10-15 → 15 000 so'm💵\n"
            "📑20-25 → 20 000 so'm💵\n"
            "📑30-40 → 30 000 so'm💵\n"
            "📑50-60 → 50 000 so'm💵\n\n"

            "👇🏻 TO'LOV KARTASI:\n"
            "💳 9860 3501 4703 9795\n"
            "👤 ABDUVAITOV SOBIR\n\n"

            "📲 To'lov qilib screenshot yuboring va tezda buyurtmangizni qabul qiling.✅",

            reply_markup=remove_keyboard
        )

        back_markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True
        )

        back_markup.add(
            "🏠 Bosh menyu"
        )

        bot.send_message(
            chat_id,
            "Bosh menyuga qaytish 👇",
            reply_markup=back_markup
        )

# ================= SCREENSHOT =================

@bot.message_handler(content_types=['photo'])
def payment_photo(message):

    chat_id = message.chat.id

    if chat_id in user_state and user_state[chat_id] == "payment":

        user_state[chat_id] = "waiting"

        bot.send_message(
            chat_id,
            "⏳ Iltimos kuting.To'lov tekshirilmoqda..."
        )

        bot.forward_message(
            ADMIN_ID,
            chat_id,
            message.message_id
        )

        markup = types.InlineKeyboardMarkup()

        approve = types.InlineKeyboardButton(
            "✅ TASDIQLASH",
            callback_data=f"approve_{chat_id}"
        )

        reject = types.InlineKeyboardButton(
            "❌ RAD ETISH",
            callback_data=f"reject_{chat_id}"
        )

        markup.add(
            approve,
            reject
        )

        bot.send_message(

            ADMIN_ID,

            f"💰 YANGI BUYURTMA.QABUL QILING \n\n"

            f"👤 MIJOZ : {chat_id}\n"
            f"📌 MAVZU : {user_data[chat_id]['topic']}\n"
            f"📄 VAROQ : {user_data[chat_id]['pages']}",

            reply_markup=markup
        )

# ================= ADMIN BUTTON =================

@bot.callback_query_handler(
    func=lambda call: True
)
def callback_handler(call):

    data = call.data

    if data.startswith(
        "approve_"
    ):

        user_id = int(
            data.split("_")[1]
        )

        pending_delivery[ADMIN_ID] = user_id

        bot.send_message(

            user_id,

            "✅ To'lov tasdiqlandi!\n"
            "📦 Buyurtmangiz tayyorlanmoqda."
        )

        bot.send_message(

            ADMIN_ID,

            "✔ Tasdiqlandi.\n\n"
            "📩 Endi BUYURTMA FAYLINI yuboring.\n"
            "(PDF 📕/ DOCX 📘/ PPTX 📙/ ZIP📒)"
        )

    elif data.startswith(
        "reject_"
    ):

        user_id = int(
            data.split("_")[1]
        )

        bot.send_message(

            user_id,

            "❌ To'lov rad etildi.\n"
            "‼️ Iltimos anniq to'lov qilganligingizga ishonch hosil qiling. ♻️"
        )

        bot.send_message(
            ADMIN_ID,
            "❌ Buyurtma rad qilindi."
        )

    bot.answer_callback_query(
        call.id
    )

# ================= FILE DELIVERY =================

@bot.message_handler(
    content_types=['document']
)
def send_file(message):

    if message.chat.id != ADMIN_ID:
        return

    if ADMIN_ID not in pending_delivery:

        bot.send_message(
            ADMIN_ID,
            "❌ Aktiv buyurtma topilmadi."
        )

        return

    user_id = pending_delivery[
        ADMIN_ID
    ]

    file_id = message.document.file_id

    bot.send_document(

        user_id,

        file_id,

        caption=
        "📦 Buyurtmangiz tayyor!\n\n"
        "Sog' bo'ling hurmatli mijoz.Sizni yana kutib qolamiz❤️"
    )

    bot.send_message(
        ADMIN_ID,
        "✅ Fayl mijozga yuborildi."
    )

    del pending_delivery[
        ADMIN_ID
    ]
#===================================================================
    @bot.message_handler(commands=['stats'])
    def stats(message):

     if message.chat.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM orders")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(price) FROM orders WHERE status='approved'")
    income = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM orders WHERE date(date)=date('now')")
    today = cursor.fetchone()[0]

    bot.send_message(
        ADMIN_ID,
        f"📊 STATISTIKA\n\n"
        f"📦 Umumiy: {total}\n"
        f"📅 Bugun: {today}\n"
        f"💰 Foyda: {income} so'm"
    )
# ================= RUN =================

print("Bot ishga tushdi...")

bot.infinity_polling()