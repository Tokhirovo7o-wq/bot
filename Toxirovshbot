from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import os
TOKEN = os.getenv("8657884258:AAEHic1P82r3ud4An42aJYbhshWQMhlHGMM")

warns = {}

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    return member.status in ["administrator", "creator"]

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

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    user_id = int(context.args[0])
    await context.bot.unban_chat_member(update.effective_chat.id, user_id)
    await update.message.reply_text("Unban qilindi ✅")

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
    user = update.message.reply_to_message.from_user
    uid = user.id
    warns[uid] = warns.get(uid, 0) + 1
    if warns[uid] >= 3:
        await context.bot.ban_chat_member(update.effective_chat.id, uid)
        warns[uid] = 0
        await update.message.reply_text(f"{user.first_name} BAN ⛔")
    else:
        await update.message.reply_text(f"Warn: {warns[uid]}/3")

async def banme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ha", callback_data="yes")],
        [InlineKeyboardButton("Yo‘q", callback_data="no")]
    ]
    await update.message.reply_text("O‘zingizni ban qilasizmi?", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "yes":
        await context.bot.ban_chat_member(query.message.chat.id, query.from_user.id)
        await query.edit_message_text("Ban bo‘ldingiz 😅")
    else:
        await query.edit_message_text("Bekor qilindi")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("banme", banme))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
