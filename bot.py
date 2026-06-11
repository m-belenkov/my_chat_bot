import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pytgpt.phind import PHIND

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN not found")

logging.basicConfig(level=logging.INFO)

# Удаляем вебхук на случай, если он был установлен ранее
try:
    resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    logging.info(f"Webhook deleted: {resp.json()}")
except Exception as e:
    logging.warning(f"Could not delete webhook: {e}")

ai_bot = PHIND()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот с ИИ. Напиши мне что-нибудь.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        reply = ai_bot.chat(user_text)
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"AI error: {e}")
        await update.message.reply_text("Ошибка при обращении к нейросети.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("Бот запущен в режиме polling")
    app.run_polling()

if __name__ == '__main__':
    main()