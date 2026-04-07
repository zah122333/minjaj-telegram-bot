import asyncio
import os
from datetime import datetime

# Updated import to use the Gregorian class for conversion
from hijridate import Gregorian
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Data storage (Note: These reset if the bot restarts on Render)
readers = []
listeners = []
excused = []

def get_today_dates():
    # Get current Gregorian date
    today_greg = datetime.today()
    gregorian_date = today_greg.strftime("%d/%m/%Y")

    # Use the Gregorian class to convert to Hijri (Fix for AttributeError)
    hijri = Gregorian(today_greg.year, today_greg.month, today_greg.day).to_hijri()

    hijri_date = f"{hijri.day}/{hijri.month}/{hijri.year}"

    return f"التاريخ 📅:\n {gregorian_date} م / {hijri_date} هـ"
    
def numbered(lst):
    if not lst:
        return "—"
    return "\n".join(f"{i+1}. {name}" for i, name in enumerate(lst))

def format_lists():
    return (
        f"{get_today_dates()}\n\n"
        f"القارئات🎤 :\n{numbered(readers)}\n\n"
        f"المستمعات👂 :\n{numbered(listeners)}\n\n"
        f"المعتذرات✖️ :\n{numbered(excused)}\n\n"
        "-----------------------------\n"
        "عن أمير المؤمنين علي بن أبي طالب (عليه السلام):\n"
        "وَأَمَّا مَا فَرَضَهُ عَلَى الأذنين: فَالإِستِمَاعُ إِلَى ذِكْرِ الله...\n"
        "— بحار الأنوار، ج90، ص49"
    )

def move_user(user, target):
    # Remove user from all lists first to avoid duplicates
    if user in readers:
        readers.remove(user)
    if user in listeners:
        listeners.remove(user)
    if user in excused:
        excused.remove(user)

    # Add to the new target list
    if target == "reader":
        readers.append(user)
    elif target == "listener":
        listeners.append(user)
    elif target == "excused":
        excused.append(user)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("سجل اسمي قارئة🎤", callback_data="reader")],
        [InlineKeyboardButton("سجل اسمي مستمعة👂", callback_data="listener")],
        [InlineKeyboardButton("سجل اسمي معتذرة✖️", callback_data="excused")],
        [InlineKeyboardButton("احذف اسمي❌", callback_data="remove")]
    ]
    await update.message.reply_text(
        format_lists(),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user.full_name
    await query.answer()

    if query.data in ["reader", "listener", "excused"]:
        move_user(user, query.data)
    elif query.data == "remove":
        move_user(user, None)

    keyboard = [
        [InlineKeyboardButton("سجل اسمي قارئة🎤", callback_data="reader")],
        [InlineKeyboardButton("سجل اسمي مستمعة👂", callback_data="listener")],
        [InlineKeyboardButton("سجل اسمي معتذرة✖️", callback_data="excused")],
        [InlineKeyboardButton("احذف اسمي❌", callback_data="remove")]
    ]

    try:
        await query.edit_message_text(
            text=format_lists(),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception:
        # Ignore errors if the message content hasn't changed
        pass

if __name__ == "__main__":
    # 1. Initialize the Application
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN environment variable not found.")
    else:
        app = ApplicationBuilder().token(token).build()

        # 2. Add Handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button))

        # 3. Handle the event loop manually for Python 3.14 stability
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        print("Bot is starting...")
        app.run_polling()
