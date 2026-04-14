import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

TOKEN = os.getenv("BOT_TOKEN")

warns = {}
users = set()
bot_messages = []

# USER TRACK
async def save_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        users.add(update.effective_user.id)

# ADMIN CHECK
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    return member.status in ["administrator", "creator"]

# START MENU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Guruhga qo‘shish", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("💀 BanAll", callback_data="banall_confirm")],
        [InlineKeyboardButton("🧹 DelAll", callback_data="delall_confirm")]
    ]

    await update.message.reply_text(
        "🤖 PRO ADMIN BOT\n\nTanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# BAN
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Faqat admin ❌")

    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply qiling ❗")

    user = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text(f"{user.first_name} ban qilindi ⛔")

# UNBAN
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("Faqat admin ❌")

    if not context.args:
        return await update.message.reply_text("ID yozing ❗")

    user_id = int(context.args[0])
    await context.bot.unban_chat_member(update.effective_chat.id, user_id)
    await update.message.reply_text("Unban qilindi ✅")

# WARN
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
        await update.message.reply_text(f"{user.first_name} → BAN ⛔")
    else:
        await update.message.reply_text(f"{user.first_name} warn: {warns[uid]}/3 ⚠️")

# BANME
async def banme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Ha", callback_data="confirm_banme")],
        [InlineKeyboardButton("❌ Yo‘q", callback_data="cancel")]
    ]
    await update.message.reply_text("O‘zingizni ban qilasizmi?", reply_markup=InlineKeyboardMarkup(keyboard))

# KICKME
async def kickme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await context.bot.unban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text("Siz chiqdingiz 👋")

# BANALL CONFIRM
async def banall_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Ha", callback_data="banall_yes")],
        [InlineKeyboardButton("❌ Yo‘q", callback_data="cancel")]
    ]
    await update.callback_query.message.reply_text("Hamma userlarni ban qilasizmi?", reply_markup=InlineKeyboardMarkup(keyboard))

# BANALL
async def banall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    count = 0

    for user_id in users:
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            if member.status in ["administrator", "creator"]:
                continue

            await context.bot.ban_chat_member(chat_id, user_id)
            count += 1
        except:
            pass

    await query.edit_message_text(f"💀 {count} ta user ban qilindi")

# DELALL CONFIRM
async def delall_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Ha", callback_data="delall_yes")],
        [InlineKeyboardButton("❌ Yo‘q", callback_data="cancel")]
    ]
    await update.callback_query.message.reply_text("Xabarlarni o‘chirasizmi?", reply_markup=InlineKeyboardMarkup(keyboard))

# DELALL
async def delall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    deleted = 0

    for msg_id in bot_messages:
        try:
            await context.bot.delete_message(chat_id, msg_id)
            deleted += 1
        except:
            pass

    await query.edit_message_text(f"🧹 {deleted} ta xabar o‘chirildi")

# BUTTON HANDLER
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "confirm_banme":
        user = query.from_user
        await context.bot.ban_chat_member(query.message.chat.id, user.id)
        await query.edit_message_text("Siz ban bo‘ldingiz 😅")

    elif query.data == "banall_confirm":
        await banall_confirm(update, context)

    elif query.data == "banall_yes":
        await banall(update, context)

    elif query.data == "delall_confirm":
        await delall_confirm(update, context)

    elif query.data == "delall_yes":
        await delall(update, context)

    elif query.data == "cancel":
        await query.answer()
        await query.edit_message_text("Bekor qilindi ✅")

# TRACK
async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        bot_messages.append(update.message.message_id)

# APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("banme", banme))
app.add_handler(CommandHandler("kickme", kickme))

app.add_handler(CallbackQueryHandler(button))

app.add_handler(MessageHandler(filters.ALL, save_users))
app.add_handler(MessageHandler(filters.ALL, track))

print("🔥 FULL PRO BOT ISHLAYAPTI")
app.run_polling()
