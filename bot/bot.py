import asyncio
import os
from datetime import datetime
from hijridate import Gregorian
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Data storage
readers = []
listeners = []
excused = []
registration_open = True 

def get_today_dates():
    today_greg = datetime.today()
    gregorian_date = today_greg.strftime("%d/%m/%Y")
    hijri = Gregorian(today_greg.year, today_greg.month, today_greg.day).to_hijri()
    hijri_date = f"{hijri.day}/{hijri.month}/{hijri.year}"
    return f"التاريخ 📅:\n {gregorian_date} م / {hijri_date} هـ"
    
def numbered(lst):
    if not lst: return "—"
    return "\n".join(f"{i+1}. {name}" for i, name in enumerate(lst))

def format_lists():
    status_msg = "" if registration_open else " ❕انتهى التسجيل في هذه القائمة\n\n"
    return (
        "قائمة الأدوار: \n\n"
        f"{status_msg}{get_today_dates()}\n\n"
        f"القارئات🎤 :\n{numbered(readers)}\n\n"
        f"المستمعات👂 :\n{numbered(listeners)}\n\n"
        f"المعتذرات✖️ :\n{numbered(excused)}\n\n"
        "-----------------------------\n"
        "عن أمير المؤمنين علي بن أبي طالب (عليه السلام):\n"
        "وَأَمَّا مَا فَرَضَهُ عَلَى الأذنين: فَالإِستِمَاعُ إِلَى ذِكْرِ الله...\n"
        "— بحار الأنوار، ج90، ص49"
    )

def get_keyboard():
    """Generates the keyboard based on whether registration is open."""
    if registration_open:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("سجل اسمي قارئة🎤", callback_data="reader")],
            [InlineKeyboardButton("سجل اسمي مستمعة👂", callback_data="listener")],
            [InlineKeyboardButton("سجل اسمي معتذرة✖️", callback_data="excused")],
            [InlineKeyboardButton("احذف اسمي❌", callback_data="remove")]
        ])
    else:
        # Only show the remove button when closed
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("احذف اسمي❌", callback_data="remove")]
        ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        format_lists(), 
        reply_markup=get_keyboard()
    )

async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global readers, listeners, excused
    readers.clear()
    listeners.clear()
    excused.clear()
    await update.message.reply_text("✅ تم مسح القائمة بالكامل.")

async def toggle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global registration_open
    registration_open = not registration_open
    status = "مفتوح ✅" if registration_open else "مغلق ❌"
    await update.message.reply_text(f"حالة التسجيل الآن: {status}")
    
    # Optional: You can send a fresh list message showing the new state
    await update.message.reply_text(format_lists(), reply_markup=get_keyboard())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user.full_name
    
    # Logic for button presses
    if query.data == "remove":
        move_user(user, None)
        await query.answer("تم حذف اسمك.")
    elif registration_open:
        move_user(user, query.data)
        await query.answer()
    else:
        await query.answer("عذراً، انتهى وقت التسجيل ❌", show_alert=True)
        return

    try:
        await query.edit_message_text(
            text=format_lists(), 
            reply_markup=get_keyboard()
        )
    except Exception:
        pass

def move_user(user, target):
    for lst in [readers, listeners, excused]:
        if user in lst: lst.remove(user)
    if target == "reader": readers.append(user)
    elif target == "listener": listeners.append(user)
    elif target == "excused": excused.append(user)

if __name__ == "__main__":
    token = os.environ.get("BOT_TOKEN")
    if token:
        app = ApplicationBuilder().token(token).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("clear", clear_list))
        app.add_handler(CommandHandler("stop", toggle_registration))
        app.add_handler(CallbackQueryHandler(button))

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        app.run_polling()
