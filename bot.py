# bot.py — ULTIMATE VERSION

import json
import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

DB_FILE = "db.json"
user_pending = {}
rate_limit = {}

DOMAIN_VIDEO = "https://infinityclouddownload.page.gd/video.php?id="
DOMAIN_AUDIO = "https://infinityclouddownload.page.gd/audio.php?id="
DOMAIN_IMAGE = "https://infinityclouddownload.page.gd/image.php?id="
DOMAIN_DOCS  = "https://infinityclouddownload.page.gd/docs.php?id="
DOMAIN_DOWNLOAD = "https://infinityclouddownload.page.gd/download.php?id="

# ================= DATABASE =================

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# ================= UTIL =================

def is_rate_limited(user_id):
    now = time.time()
    if user_id in rate_limit and now - rate_limit[user_id] < 1:
        return True
    rate_limit[user_id] = now
    return False

def format_size(size):
    try:
        return f"{round(size/1024/1024,2)} MB"
    except:
        return "Unknown"

# ================= COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Infinity Cloud Bot\n\n"
        "📤 Send file → Send keyword → Done\n"
        "🔍 Use /search keyword\n"
        "📌 /help for commands"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Commands:\n"
        "/search keyword\n"
        "/delete keyword\n"
        "/stats\n"
        "/help"
    )

# ================= FILE HANDLER =================

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    file = msg.document or msg.video or msg.audio

    if not file:
        return

    user_pending[msg.from_user.id] = {
        "id": file.file_id,
        "name": getattr(file, "file_name", "file"),
        "size": getattr(file, "file_size", 0)
    }

    await msg.reply_text("📌 Send keyword for this file")

# ================= SAVE KEYWORD =================

async def save_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_pending:
        return

    keyword = update.message.text.lower()
    data = user_pending[user_id]

    db = load_db()

    if keyword not in db:
        db[keyword] = []

    db[keyword].append({
        "id": data["id"],
        "name": data["name"],
        "size": data["size"],
        "views": 0
    })

    save_db(db)
    del user_pending[user_id]

    await update.message.reply_text(f"✅ Saved under: {keyword}")

# ================= SEARCH =================

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if is_rate_limited(user_id):
        return

    if not context.args:
        await update.message.reply_text("❌ Use: /search keyword")
        return

    query = " ".join(context.args).lower()
    db = load_db()

    results = []

    for key in db:
        if query in key:
            results.append((key, db[key]))

    if not results:
        await update.message.reply_text("❌ Not found")
        return

    for key, files in results:
        for f in files:
            file_id = f["id"]

            try:
                tg_file = await context.bot.get_file(file_id)
                path = tg_file.file_path.lower()
            except:
                path = ""

            if path.endswith((".mp4",".mkv",".webm")):
                view = DOMAIN_VIDEO + file_id
            elif path.endswith((".mp3",".wav")):
                view = DOMAIN_AUDIO + file_id
            elif path.endswith((".jpg",".jpeg",".png",".webp")):
                view = DOMAIN_IMAGE + file_id
            else:
                view = DOMAIN_DOCS + file_id

            download = DOMAIN_DOWNLOAD + file_id

            text = (
                f"📂 {key}\n"
                f"📄 {f['name']}\n"
                f"💾 {format_size(f['size'])}\n"
                f"👁 {f['views']}"
            )

            buttons = [
                [
                    InlineKeyboardButton("🎬 Open", url=view),
                    InlineKeyboardButton("⬇ Download", url=download)
                ]
            ]

            await update.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

# ================= DELETE =================

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: /delete keyword")
        return

    keyword = " ".join(context.args).lower()
    db = load_db()

    if keyword not in db:
        await update.message.reply_text("Not found")
        return

    del db[keyword]
    save_db(db)

    await update.message.reply_text("Deleted")

# ================= STATS =================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    total = sum(len(v) for v in db.values())

    await update.message.reply_text(
        f"📊 Stats\n\n"
        f"Keywords: {len(db)}\n"
        f"Files: {total}"
    )

# ================= APP =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("search", search))
app.add_handler(CommandHandler("delete", delete))
app.add_handler(CommandHandler("stats", stats))

app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO | filters.AUDIO, handle_file))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_keyword))

app.run_polling()
