import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

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

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.video or update.message.photo
    
    if file:
        context.user_data["file_id"] = file.file_id
        await update.message.reply_text("📌 Send keyword to save this file")

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

async def search(update: Update
