from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime
from hijri.core import Hijriah

readers = []
listeners = []
excused = []


def get_today_dates():
    today_greg = datetime.today()
    gregorian_date = today_greg.strftime("%d/%m/%Y")

    hijri = Hijriah(day=today_greg.day, month=today_greg.month, year=today_greg.year)
    hijri_date = hijri.to_hijri()

    return f"📅 التاريخ: {gregorian_date} م / {hijri_date} هـ"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("سجل اسمي قارئة", callback_data="reader")],
        [InlineKeyboardButton("سجل اسمي مستمعة", callback_data="listener")],
        [InlineKeyboardButton("سجل اسمي معتذرة", callback_data="excused")],
        [InlineKeyboardButton("احذف اسمي", callback_data="remove")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(format_lists(), reply_markup=reply_markup)


def format_lists():
    return (
            f"{get_today_dates()}\n\n"
            f"📖 القارئات:\n" + "\n".join(readers) + "\n\n"
            f"👂 المستمعات:\n" + "\n".join(listeners) + "\n\n"
            f"❌ المعتذرات:\n" + "\n".join(excused) + "\n\n"
    )


def move_user_to_list(user, target_list):
    if user in readers: readers.remove(user)
    if user in listeners: listeners.remove(user)
    if user in excused: excused.remove(user)
    if target_list == "reader":
        readers.append(user)
    elif target_list == "listener":
        listeners.append(user)
    elif target_list == "excused":
        excused.append(user)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user.full_name
    await query.answer()

    if query.data in ['reader', 'listener', 'excused']:
        move_user_to_list(user, query.data)
    elif query.data == 'remove':
        move_user_to_list(user, None)

    await query.edit_message_text(text=format_lists(), reply_markup=query.message.reply_markup)


# هنا نستخدم ApplicationBuilder بدل Updater
app = ApplicationBuilder().token("8682386038:AAHBQqHU_x1OwPRrwR6SpYGyJqCfiopIUB4").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()

