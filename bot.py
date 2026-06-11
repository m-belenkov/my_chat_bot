import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pytgpt.phind import PHIND

# --- 1. НАСТРОЙКА ---
# Получаем токен бота из переменной окружения (Bothost подставит его автоматически)
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не найдена. Укажите токен в настройках бота на Bothost.")

# Включаем логирование, чтобы видеть, что бот делает (поможет при отладке)
logging.basicConfig(level=logging.INFO)

# Инициализируем AI-помощника (используем Phind — бесплатный LLM-провайдер)
ai_bot = PHIND()

# --- 2. ФУНКЦИИ-ОБРАБОТЧИКИ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие при команде /start"""
    await update.message.reply_text(
        "Привет! Я бот с искусственным интеллектом. 🤖\n"
        "Напиши мне любое сообщение, и я отвечу.\n"
        "Доступные команды:\n"
        "/start — приветствие\n"
        "/help — справка\n"
        "/about — информация о боте"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка"""
    await update.message.reply_text(
        "Просто отправь мне текст, и я передам его нейросети.\n"
        "Я отвечаю на вопросы, могу написать код, пересказать текст и многое другое."
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о боте"""
    await update.message.reply_text(
        "🤖 Этот бот создан для учебного проекта.\n"
        "Используется библиотека python-tgpt с провайдером Phind.\n"
        "Бот работает на платформе Bothost.ru и доступен 24/7."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка любого текстового сообщения"""
    user_text = update.message.text
    # Отправляем уведомление "печатает", чтобы пользователь видел, что бот обрабатывает
    await update.message.chat.send_action(action="typing")
    
    try:
        # Запрос к LLM через python-tgpt
        ai_response = ai_bot.chat(user_text)
        # Отправляем ответ пользователю
        await update.message.reply_text(ai_response)
    except Exception as e:
        logging.error(f"Ошибка при обращении к LLM: {e}")
        await update.message.reply_text(
            "Извините, произошла ошибка при обращении к нейросети. 😞\n"
            "Попробуйте позже или обратитесь к администратору."
        )

# --- 3. ЗАПУСК БОТА ---
def main():
    # Создаём приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))

    # Регистрируем обработчик всех текстовых сообщений (кроме команд)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота (polling — не нужен ни порт, ни домен)
    print("Бот запущен и работает через polling...")
    application.run_polling()

if __name__ == '__main__':
    main()