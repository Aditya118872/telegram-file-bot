import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# 🔗 अपना domain यहाँ डाल
DOMAIN = "https://infinityclouddownload.page.gd/download.php?id="

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

# 🟢 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Setup:\n\n1. Private group बनाओ\n2. Bot को admin बनाओ\n3. Group में file upload करो\n\n🔍 फिर use करो:\n/search filename"
    )

# 🟢 Group में file detect
async def handle_group_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type not in ["group", "supergroup"]:
        return

    msg = update.message

    file = None
    filename = "file"

    if msg.document:
        file = msg.document
        filename = msg.document.file_name.lower()

    elif msg.video:
        file = msg.video
        filename = "video"

    elif msg.photo:
        file = msg.photo[-1]
        filename = "image"

    if file:
        file_id = file.file_id

        db = load_db()

        if filename not in db:
            db[filename] = []

        db[filename].append(file_id)
        save_db(db)

        await msg.reply_text(f"✅ Saved: {filename}")

# 🟢 Search command
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: /search filename")
        return

    keyword = " ".join(context.args).lower()
    db = load_db()

    if keyword not in db:
        await update.message.reply_text("❌ File not found")
        return

    for file_id in db[keyword]:
        link = f"{DOMAIN}{file_id}"
        await update.message.reply_text(f"📥 Download:\n{link}")

# 🚀 Bot start
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search))
app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO | filters.PHOTO, handle_group_file))

app.run_polling()
