import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

TOKEN = os.getenv("BOT_TOKEN")

# ===================== PER GROUP DATABASE =====================
group_data = {}

def get_group(chat_id):
    if chat_id not in group_data:
        group_data[chat_id] = {
            "users": set(),
            "warns": {},
            "muted": set()
        }
    return group_data[chat_id]

# ===================== ADMIN CHECK =====================
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    return member.status in ["administrator", "creator"]

# ===================== USER TRACK =====================
async def track_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return
    chat_id = update.effective_chat.id
    data = get_group(chat_id)

    data["users"].add(update.effective_user.id)

# ===================== AUTO DELETE SYSTEM =====================
async def auto_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = update.effective_chat.id
    data = get_group(chat_id)

    if update.effective_user.id in data["muted"]:
        try:
            await update.message.delete()
        except:
            pass

# ===================== START MENU =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Guruhga qo‘shish", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("💀 BanAll", callback_data="banall")],
        [InlineKeyboardButton("🧹 DelAll", callback_data="delall")]
    ]

    await update.message.reply_text(
        "🤖 FULL PRO ADMIN BOT\n\nTanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===================== OLD FUNCS =====================

# BANME
async def banme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Ha", callback_data="banme_yes")],
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
    await update.message.reply_text("👋 Siz chiqdingiz")

# ===================== DOT COMMANDS =====================
async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    if not text.startswith("."):
        return

    cmd = text.split()[0].lower()
    chat_id = update.effective_chat.id
    data = get_group(chat_id)

    # ================= .ban =================
    if cmd == ".ban":
        if not await is_admin(update, context):
            return

        if not update.message.reply_to_message:
            return await update.message.reply_text("Reply qiling ❗")

        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(chat_id, user.id)
        await update.message.reply_text(f"{user.first_name} ban qilindi ⛔")

    # ================= .unban =================
    elif cmd == ".unban":
        if not await is_admin(update, context):
            return

        if not context.args:
            return await update.message.reply_text("ID yozing ❗")

        user_id = int(context.args[0])
        await context.bot.unban_chat_member(chat_id, user_id)
        await update.message.reply_text("Unban qilindi ✅")

    # ================= .warn =================
    elif cmd == ".warn":
        if not await is_admin(update, context):
            return

        if not update.message.reply_to_message:
            return

        user = update.message.reply_to_message.from_user
        uid = user.id

        data["warns"][uid] = data["warns"].get(uid, 0) + 1

        if data["warns"][uid] >= 3:
            await context.bot.ban_chat_member(chat_id, uid)
            data["warns"][uid] = 0
            await update.message.reply_text(f"{user.first_name} → BAN ⛔")
        else:
            await update.message.reply_text(f"{user.first_name} warn: {data['warns'][uid]}/3 ⚠️")

    # ================= .banall =================
    elif cmd == ".banall":
        if not await is_admin(update, context):
            return

        count = 0

        for user_id in data["users"]:
            try:
                member = await context.bot.get_chat_member(chat_id, user_id)

                if member.status in ["administrator", "creator"]:
                    continue

                await context.bot.ban_chat_member(chat_id, user_id)
                count += 1
            except:
                pass

        await update.message.reply_text(f"💀 {count} ta user ban qilindi")

    # ================= .delall =================
    elif cmd == ".delall":
        if not await is_admin(update, context):
            return

        if not update.message.reply_to_message:
            return await update.message.reply_text("Reply qiling ❗")

        user = update.message.reply_to_message.from_user
        data["muted"].add(user.id)

        await update.message.reply_text(f"{user.first_name} → barcha xabarlari o‘chiriladi 🧹")

    # ================= .info =================
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

    if query.data == "banme_yes":
        user = query.from_user
        await context.bot.ban_chat_member(query.message.chat.id, user.id)
        await query.edit_message_text("Siz ban bo‘ldingiz 😅")

    elif query.data == "cancel":
        await query.edit_message_text("Bekor qilindi ✅")

    elif query.data == "banall":
        await query.edit_message_text("⚠️ .banall ni command bilan ishlating")

    elif query.data == "delall":
        await query.edit_message_text("⚠️ .delall ni command bilan ishlating")

# ===================== RUN =====================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("banme", banme))
app.add_handler(CommandHandler("kickme", kickme))

app.add_handler(MessageHandler(filters.TEXT, commands))
app.add_handler(MessageHandler(filters.ALL, track_users))
app.add_handler(MessageHandler(filters.ALL, auto_delete))

app.add_handler(CallbackQueryHandler(button))

print("🔥 FULL PRO BOT READY (PER GROUP)")
app.run_polling()
