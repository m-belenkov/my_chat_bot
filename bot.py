# bot.py
import os
import json
import logging
import requests
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- НАСТРОЙКИ (берутся из переменных окружения) ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

if not TELEGRAM_TOKEN or not WEBHOOK_URL or not OPENROUTER_API_KEY:
    raise ValueError("Отсутствуют необходимые переменные окружения!")

# Настройка логирования для отладки
logging.basicConfig(level=logging.INFO)

# --- ИНИЦИАЛИЗАЦИЯ ---
flask_app = Flask(__name__)
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

# --- ОБРАБОТЧИКИ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение по команде /start"""
    await update.message.reply_text(
        "Привет! Я ИИ-бот. Напиши мне что-нибудь.\n"
        "Использую модели Mistral, Gemma, DeepSeek и другие через OpenRouter."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет сообщение пользователя в выбранную LLM и возвращает ответ"""
    user_text = update.message.text
    await update.message.chat.send_action(action="typing")
    try:
        # Запрос к OpenRouter API
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [{"role": "user", "content": user_text}],
            }
        )
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"Ошибка при обращении к OpenRouter API: {e}")
        await update.message.reply_text("Извините, произошла ошибка при обработке запроса. Попробуйте позже.")

# Регистрируем обработчики в приложении telegram
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- ВЕБХУК ДЛЯ FLASK ---
@flask_app.route('/webhook', methods=['POST'])
async def webhook():
    """Принимает входящие обновления от Telegram"""
    try:
        update_data = request.get_json()
        update = Update.de_json(update_data, telegram_app.bot)
        await telegram_app.process_update(update)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logging.error(f"Ошибка в вебхуке: {e}")
        return jsonify({"status": "error"}), 500

# --- ТОЧКА ВХОДА ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    webhook_url = f"{WEBHOOK_URL}/webhook"
    
    # Устанавливаем вебхук в Telegram
    try:
        r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}")
        logging.info(f"Установка вебхука: {r.json()}")
    except Exception as e:
        logging.error(f"Не удалось установить вебхук: {e}")
    
    logging.info(f"🚀 Бот запущен на порту {port}")
    flask_app.run(host="0.0.0.0", port=port)