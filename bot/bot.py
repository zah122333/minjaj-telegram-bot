from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("8682386038:AAFvTc88hKRAgWIpC1rZi95pK9iQaJ62Xhk")

readers = []
listeners = []
excused = []

registration_open = True


# عرض القائمة مع الأزرار
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("سجل اسمي قارئة", callback_data="reader")],
        [InlineKeyboardButton("سجل اسمي مستمعة", callback_data="listener")],
        [InlineKeyboardButton("سجل اسمي معتذرة", callback_data="excused")],
        [InlineKeyboardButton("احذف اسمي", callback_data="remove")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "📋 قائمة التسجيل:\n\n"
        f"📖 القارئات:\n" + ("\n".join(readers) if readers else "لا يوجد") + "\n\n"
        f"👂 المستمعات:\n" + ("\n".join(listeners) if listeners else "لا يوجد") + "\n\n"
        f"❗ المعتذرات:\n" + ("\n".join(excused) if excused else "لا يوجد")
    )

    await update.message.reply_text(text, reply_markup=reply_markup)


# التعامل مع الأزرار
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global registration_open

    query = update.callback_query
    user = query.from_user.full_name

    await query.answer()

    if not registration_open:
        await query.answer("التسجيل مغلق حالياً ❌", show_alert=True)
        return

    # إزالة الاسم من كل القوائم أولاً
    if user in readers:
        readers.remove(user)
    if user in listeners:
        listeners.remove(user)
    if user in excused:
        excused.remove(user)

    if query.data == "reader":
        readers.append(user)
    elif query.data == "listener":
        listeners.append(user)
    elif query.data == "excused":
        excused.append(user)
    elif query.data == "remove":
        pass

    text = (
        "📋 قائمة التسجيل:\n\n"
        f"📖 القارئات:\n" + ("\n".join(readers) if readers else "لا يوجد") + "\n\n"
        f"👂 المستمعات:\n" + ("\n".join(listeners) if listeners else "لا يوجد") + "\n\n"
        f"❗ المعتذرات:\n" + ("\n".join(excused) if excused else "لا يوجد")
    )

    await query.edit_message_text(text=text, reply_markup=query.message.reply_markup)


# التحقق هل المستخدم أدمن
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
    return chat_member.status in ["administrator", "creator"]


# إيقاف التسجيل
async def close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global registration_open
    if not await is_admin(update, context):
        await update.message.reply_text("هذا الأمر للمشرفات فقط ❌")
        return

    registration_open = False
    await update.message.reply_text("تم إيقاف التسجيل ✋")


# فتح التسجيل
async def open_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global registration_open
    if not await is_admin(update, context):
        await update.message.reply_text("هذا الأمر للمشرفات فقط ❌")
        return

    registration_open = True
    await update.message.reply_text("تم فتح التسجيل من جديد ✅")


# حذف القائمة
async def delete_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global readers, listeners, excused

    if not await is_admin(update, context):
        await update.message.reply_text("هذا الأمر للمشرفات فقط ❌")
        return

    readers.clear()
    listeners.clear()
    excused.clear()

    await update.message.reply_text("تم حذف القائمة بالكامل 🗑️")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("close", close))
app.add_handler(CommandHandler("open", open_registration))
app.add_handler(CommandHandler("deletelist", delete_list))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
