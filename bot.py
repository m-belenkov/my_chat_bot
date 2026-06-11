import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pytgpt.phind import PHIND

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена.")

logging.basicConfig(level=logging.INFO)

# Инициализация AI
ai_bot = PHIND()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот с искусственным интеллектом. 🤖\nНапиши мне что-нибудь.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        reply = ai_bot.chat(user_text)
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"AI error: {e}")
        await update.message.reply_text("Ошибка при обращении к нейросети. Попробуйте позже.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Получаем порт из переменной окружения (Bothost передаёт PORT=3000)
    port = int(os.environ.get('PORT', 3000))
    # Определяем домен (Bothost передаёт BOTHOST_DOMAIN или используем вручную)
    domain = os.environ.get('BOTHOST_DOMAIN', 'mybot.bothost.tech')
    webhook_url = f"https://{domain}/webhook"

    # Запускаем вебхук
    app.run_webhook(listen="0.0.0.0", port=port, webhook_url=webhook_url)
    logging.info(f"Бот запущен в режиме webhook на порту {port}, URL: {webhook_url}")

if __name__ == '__main__':
    main()