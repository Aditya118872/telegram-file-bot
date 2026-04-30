import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "db.json"
DOMAIN = "https://infinityclouddownload.page.gd/download.php?id="

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
    await update.message.reply_text("Upload file in group → then use /search filename")

async def handle_group_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type in ["group", "supergroup"]:
        msg = update.message
        file = msg.document or msg.video or (msg.photo[-1] if msg.photo else None)

        if file:
            file_id = file.file_id
            name = msg.document.file_name.lower() if msg.document else "file"

            db = load_db()
            if name not in db:
                db[name] = []

            db[name].append(file_id)
            save_db(db)

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: /search filename")
        return

    keyword = " ".join(context.args).lower()
    db = load_db()

    if keyword not in db:
        await update.message.reply_text("❌ Not found")
        return

    for file_id in db[keyword]:
        link = f"{DOMAIN}{file_id}"
        await update.message.reply_text(f"📥 Download:\n{link}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search))
app.add_handler(MessageHandler(filters.ALL, handle_group_file))

app.run_polling()
