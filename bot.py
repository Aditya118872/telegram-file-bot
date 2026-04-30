import json
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "db.json"

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Send file → send keyword → /search keyword")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    file = msg.document or msg.video or (msg.photo[-1] if msg.photo else None)

    if file:
        context.user_data["file_id"] = file.file_id
        await msg.reply_text("📌 Send keyword to save this file")

async def save_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "file_id" not in context.user_data:
        return

    keyword = update.message.text.lower()
    file_id = context.user_data["file_id"]

    db = load_db()

    if keyword not in db:
        db[keyword] = []

    db[keyword].append(file_id)
    save_db(db)

    del context.user_data["file_id"]

    await update.message.reply_text(f"✅ Saved under: {keyword}")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Use: /search keyword")
        return

    keyword = " ".join(context.args).lower()
    db = load_db()

    if keyword not in db:
        await update.message.reply_text("❌ Not found")
        return

    for file_id in db[keyword]:
        file = await context.bot.get_file(file_id)
        link = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
        await update.message.reply_text(f"📥 Download:\n{link}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search))
app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO | filters.PHOTO, handle_file))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_keyword))

app.run_polling()
