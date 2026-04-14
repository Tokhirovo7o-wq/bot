import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

TOKEN = os.getenv("BOT_TOKEN")

warns = {}
users = set()
muted_users = set()

# ===================== ADMIN CHECK =====================
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    return member.status in ["administrator", "creator"]

# ===================== TRACK USERS =====================
async def track_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        users.add(update.effective_user.id)

# ===================== AUTO DELETE =====================
async def auto_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.effective_user.id in muted_users:
        try:
            await update.message.delete()
        except:
            pass

# ===================== START MENU =====================
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

# ===================== OLD COMMANDS =====================

# BANME
async def banme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Ha", callback_data="confirm_banme")],
        [InlineKeyboardButton("❌ Yo‘q", callback_data="cancel")]
    ]
    await update.message.reply_text(
        "O‘zingizni ban qilasizmi?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# KICKME
async def kickme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    await context.bot.unban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text("Siz chiqdingiz 👋")

# ===================== DOT COMMANDS =====================
async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    if not text.startswith("."):
        return

    cmd = text.split()[0].lower()

    # .ban
    if cmd == ".ban":
        if not await is_admin(update, context):
            return
        if not update.message.reply_to_message:
            return await update.message.reply_text("Reply qiling ❗")

        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"{user.first_name} ban qilindi ⛔")

    # .unban
    elif cmd == ".unban":
        if not await is_admin(update, context):
            return
        if not context.args:
            return await update.message.reply_text("ID yozing ❗")

        user_id = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text("Unban qilindi ✅")

    # .warn
    elif cmd == ".warn":
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

    # .banall
    elif cmd == ".banall":
        if not await is_admin(update, context):
            return

        count = 0
        for user_id in users:
            try:
                member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
                if member.status in ["administrator", "creator"]:
                    continue

                await context.bot.ban_chat_member(update.effective_chat.id, user_id)
                count += 1
            except:
                pass

        await update.message.reply_text(f"💀 {count} ta user ban qilindi")

    # .delall
    elif cmd == ".delall":
        if not await is_admin(update, context):
            return
        if not update.message.reply_to_message:
            return await update.message.reply_text("Reply qiling ❗")

        user = update.message.reply_to_message.from_user
        muted_users.add(user.id)

        await update.message.reply_text(f"{user.first_name} xabarlari endi o‘chiriladi 🧹")

    # .info
    elif cmd == ".info":
        if update.message.reply_to_message:
            user = update.message.reply_to_message.from_user
        else:
            user = update.effective_user

        text = (
            "👤 USER INFO\n\n"
            f"🆔 ID: {user.id}\n"
            f"👤 Name: {user.first_name}\n"
            f"👤 Last: {user.last_name}\n"
            f"🔗 Username: @{user.username if user.username else 'yo‘q'}\n"
            f"🤖 Bot: {user.is_bot}\n"
            f"⭐ Premium: {getattr(user, 'is_premium', False)}\n"
            f"🌐 Link: tg://user?id={user.id}"
        )

        await update.message.reply_text(text)

# ===================== CALLBACK BUTTONS =====================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_banme":
        user = query.from_user
        await context.bot.ban_chat_member(query.message.chat.id, user.id)
        await query.edit_message_text("Siz ban bo‘ldingiz 😅")

    elif query.data == "cancel":
        await query.edit_message_text("Bekor qilindi ✅")

# ===================== RUN =====================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

# old commands
app.add_handler(CommandHandler("banme", banme))
app.add_handler(CommandHandler("kickme", kickme))

# dot system
app.add_handler(MessageHandler(filters.TEXT, commands))

# tracking
app.add_handler(MessageHandler(filters.ALL, track_users))
app.add_handler(MessageHandler(filters.ALL, auto_delete))

# buttons
app.add_handler(CallbackQueryHandler(button))

print("🔥 FULL PRO BOT READY")
app.run_polling()
