import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# 🔑 TOKEN (Railway Variablesdan olinadi)
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("❌ BOT_TOKEN topilmadi! Railway Variablesni tekshir")

# 📊 warn system
warns = {}

# 🛡 ADMIN TEKSHIRISH
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    return member.status in ["administrator", "creator"]

# ⛔ BAN
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("Faqat admin ❌")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply qiling ❗")
        return

    user = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text(f"{user.first_name} ban qilindi ⛔")

# ✅ UNBAN
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("Faqat admin ❌")
        return

    if not context.args:
        await update.message.reply_text("User ID yozing ❗")
        return

    user_id = int(context.args[0])
    await context.bot.unban_chat_member(update.effective_chat.id, user_id)
    await update.message.reply_text("Unban qilindi ✅")

# ⚠️ WARN SYSTEM
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user
    uid = user.id

    warns[uid] = warns.get(uid, 0) + 1

    if warns[uid] >= 3:
        await context.bot.ban_chat_member(update.effective_chat.id, uid)
        warns[uid] = 0
        await update.message.reply_text(f"{user.first_name} 3 ta warn → BAN ⛔")
    else:
        await update.message.reply_text(f"{user.first_name} warn: {warns[uid]}/3 ⚠️")

# 🚫 BANME COMMAND
async def banme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Ha ban qil", callback_data="confirm_banme")],
        [InlineKeyboardButton("❌ Yo‘q", callback_data="cancel")]
    ]

    await update.message.reply_text(
        "O‘zingizni ban qilasizmi?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔘 BUTTON HANDLER
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_banme":
        user = query.from_user
        await context.bot.ban_chat_member(query.message.chat.id, user.id)
        await query.edit_message_text("Siz ban bo‘ldingiz 😅")

    elif query.data == "cancel":
        await query.edit_message_text("Bekor qilindi ✅")

# 👋 KICKME
async def kickme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await context.bot.unban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text("Siz chiqdingiz 👋")

# 🚀 START BOT
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("banme", banme))
    app.add_handler(CommandHandler("kickme", kickme))
    app.add_handler(CallbackQueryHandler(button))

    print("🚀 SUPER BOT ISHGA TUSHDI")
    app.run_polling()

if __name__ == "__main__":
    main()
