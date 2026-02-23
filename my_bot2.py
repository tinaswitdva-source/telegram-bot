from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

from bot_template import get_template_text
from text_processing import (
    text_match_percentage,
    get_level_from_percentage
)

TOKEN = "8370524854:AAHDz0BOUesPdWKDTxNyXP0i7-Wc4zsjtRE"

# ======================
# КОНСТАНТИ ТЕКСТІВ UI
# ======================

START_TEXT = "Вітаю, давай розпочнемо, тисни кнопку"

BTN_PLAYING = "Отримати результат розшифровки тексту 📝"
BTN_PLAYED = "Я вже зіграв 👌"

BTN_BACK = "Повернутися в меню ↩️"

BTN_EXTRA = "Хочу додаткові матеріали 🖼️"
BTN_SHOW_TEXT = "Хочу рошифрований текст листівки 📜"

SEND_TEXT_PROMPT = (
    "Надішли в повідомленні текст з листівки\n"
    "💡Примітка: замість 'ы' можна друкувати 'ьі' або 'и', "
    "замість 'э' – 'е'"
)
TEXT_RECEIVED = "Текст отримано, опрацювання тексту — {percent:.2f}%\n\nРівень {level}"
TEXT_AGAIN = "Якщо хочеш текст прислати ще раз, натисни кнопку знову 👇"
CODE_PROMPT = "Ок, напиши в повідомленні кодове слово 🔍"
WRONG_CODE = "Неправильне кодове слово ❌\nСпробуй ще"
STAR_QUESTION = "Чи ти розгадав слова, позначені в тексті листівки зірочкою * ?"
CONGRATS = "Молодець ✅"
TRY_NEXT_TIME = "Щасти наступного разу 👋"

# ======================
# КЛАВІАТУРИ
# ======================

main_menu = [[BTN_PLAYING, BTN_PLAYED]]
played_menu = [[BTN_EXTRA], [BTN_SHOW_TEXT], [BTN_BACK]]

main_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
played_markup = ReplyKeyboardMarkup(played_menu, resize_keyboard=True)
answer_star_markup = ReplyKeyboardMarkup([["Так", "Ні"]], resize_keyboard=True, one_time_keyboard=True)

# ======================
# /start
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_text"] = False
    context.user_data["waiting_code"] = False
    context.user_data["waiting_answer_star"] = False

    first_start = context.user_data.get("first_start", True)
    context.user_data["first_start"] = False

    if first_start:
        await update.message.reply_text(
            START_TEXT,
            reply_markup=main_markup
        )
    else:
        await update.message.reply_text(
            "Обери дію 👀",
            reply_markup=main_markup
        )

# ======================
# ОБРОБКА КНОПОК І ТЕКСТУ
# ======================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # --- Головне меню ---
    if text == BTN_PLAYING:
        context.user_data["waiting_text"] = True
        context.user_data["waiting_code"] = False
        await update.message.reply_text(SEND_TEXT_PROMPT)
        return

    elif text == BTN_PLAYED:
        context.user_data["waiting_code"] = True
        context.user_data["waiting_text"] = False
        await update.message.reply_text(CODE_PROMPT)
        return

    # --- Рошифровка тексту (тільки після кнопки) ---
    if context.user_data.get("waiting_text"):
        template_text = get_template_text()
        percent = text_match_percentage(text, template_text)
        level = get_level_from_percentage(percent)
        await update.message.reply_text(
            TEXT_RECEIVED.format(percent=percent, level=level),
            parse_mode="HTML"
        )
        await update.message.reply_text(TEXT_AGAIN)
        # Скидаємо прапорець і повертаємо головне меню
        context.user_data["waiting_text"] = False
        await update.message.reply_text("Обери дію 👀", reply_markup=main_markup)
        return

    # --- Кодове слово ---
    if context.user_data.get("waiting_code"):
        if text.lower() == "алушта":
            context.user_data["waiting_code"] = False
            context.user_data["waiting_text"] = False
            await update.message.reply_text("Кодове слово правильне ✅", reply_markup=played_markup)
        else:
            await update.message.reply_text(WRONG_CODE)
        return

    # --- Відповідь на зірочки ---
    if context.user_data.get("waiting_answer_star"):
        if text == "Так":
            context.user_data["waiting_answer_star"] = False
            await update.message.reply_text(CONGRATS, reply_markup=played_markup)
        elif text == "Ні":
            context.user_data["waiting_answer_star"] = False
            await update.message.reply_text(TRY_NEXT_TIME, reply_markup=played_markup)
        else:
            await update.message.reply_text(STAR_QUESTION, reply_markup=answer_star_markup)
        return

    # --- Підменю «Я вже зіграв» ---
    if text in [BTN_EXTRA, BTN_SHOW_TEXT, BTN_BACK]:
        if text == BTN_EXTRA:
            # ===== Надсилання прямих лінків з підписами =====
            drive_links = [
                ("https://drive.google.com/uc?id=1fk2rFUVFUPpZJz1tdumtR1XB4ulYJiBt", "Одеська обласна філармонія в історичному центрі міста займає одну з найкрасивіших будівель 1899 (купецька біржа) по вул.Італійська 17"),
                ("https://drive.google.com/uc?id=1NQiIpqpaGo8plQluUWgbZmEDXSeTkKBx", "Одеська філармонія 1957 р"),
                ("https://drive.google.com/uc?id=1u9tUFQUh4fQFGkVXBdrQ0RoRu1LZV4oX", "Одеський аеропорт. Одеса. Фото 3/III-62 г. Фатеев (4419)Джерело - сайт https://viknaodessa.od.ua/odessa-archives/?odesskij-aeroport-archive"),
                ("https://drive.google.com/uc?id=1tTBF03TWQWADMQ32c_oTtvjh3KjOgZLT", "На вулицях Одеси в 60-ті"),
                ("https://drive.google.com/uc?id=1XNKANwLdnnBogdOcEddQcZ5KxuP7txzX", "Гіпотетичний портрет автора листівки, створений за допомогою ШІ"),

            ]
            
            for link, caption in drive_links:
                await update.message.reply_photo(photo=link, caption=caption)

        elif text == BTN_SHOW_TEXT:
            template_text = get_template_text()
            await update.message.reply_text("Ось текст листівки 📜👇")
            await update.message.reply_text(template_text)
            await update.message.reply_text(STAR_QUESTION, reply_markup=answer_star_markup)
            context.user_data["waiting_answer_star"] = True
        elif text == BTN_BACK:
            context.user_data["waiting_text"] = False
            context.user_data["waiting_code"] = False
            context.user_data["waiting_answer_star"] = False
            await start(update, context)
        return

    # --- Фолбек — завжди головне меню ---
    await update.message.reply_text("Обери дію 👀", reply_markup=main_markup)

# ======================
# ЗАПУСК БОТА
# ======================

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

print("Бот стартує...")
app.run_polling()