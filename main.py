import logging
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN
from database import load_bikes
from handlers import (
    start, budget_handler, type_handler, power_handler,
    handle_budget_selection, handle_type_selection, handle_power_selection,
    pagination, edit_params, edit_budget, edit_type, edit_power,
    back_to_edit, cancel_edit, restart, restart_command, help_command, handle_main_buttons,
    handle_mode_custom
)
from conversation import get_conversation_handler

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def set_menu_commands(app: Application) -> None:
    """Установит меню команд для бота"""
    commands = [
        BotCommand("start", "🏠 Найти мотоцикл"),
        BotCommand("restart", "🔄 Перезапуск"),
        BotCommand("help", "ℹ️ Справка")
    ]
    await app.bot.set_my_commands(commands)

def main():
    bikes = load_bikes()
    if not bikes:
        logger.error("❌ Нет данных! Проверьте bikes.json")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Команды
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('restart', restart_command))
    app.add_handler(CommandHandler('help', help_command))

    # ConversationHandler должен быть ПЕРВЫМ для приоритета
    app.add_handler(get_conversation_handler())

    # Обработчик выбора режима "По своей последовательности"
    app.add_handler(CallbackQueryHandler(handle_mode_custom, pattern='^mode_custom$'))

    # Обработчики для выбора параметров (работают всегда)
    app.add_handler(CallbackQueryHandler(handle_budget_selection, pattern='^budget_'))
    app.add_handler(CallbackQueryHandler(handle_type_selection, pattern='^type_'))
    app.add_handler(CallbackQueryHandler(handle_power_selection, pattern='^power_'))

    # Обработчики пагинации и редактирования
    app.add_handler(CallbackQueryHandler(pagination, pattern='^page_'))
    app.add_handler(CallbackQueryHandler(edit_params, pattern='^edit_params$'))
    app.add_handler(CallbackQueryHandler(edit_budget, pattern='^edit_budget$'))
    app.add_handler(CallbackQueryHandler(edit_type, pattern='^edit_type$'))
    app.add_handler(CallbackQueryHandler(edit_power, pattern='^edit_power$'))
    app.add_handler(CallbackQueryHandler(back_to_edit, pattern='^back_to_edit$'))
    app.add_handler(CallbackQueryHandler(cancel_edit, pattern='^cancel_edit$'))
    app.add_handler(CallbackQueryHandler(restart, pattern='^restart$'))

    # Обработчик текстовых сообщений (reply-клавиатура)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_buttons))

    # Установим меню команд
    app.post_init = set_menu_commands

    logger.info("🚀 Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()