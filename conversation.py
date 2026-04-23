from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler
from config import BUDGET, TYPE, POWER
from handlers import start, budget_handler, type_handler, power_handler, restart, handle_mode_step_by_step

def get_conversation_handler():
    conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CallbackQueryHandler(handle_mode_step_by_step, pattern='^mode_step_by_step$')
        ],
        states={
            BUDGET: [
                CallbackQueryHandler(budget_handler, pattern='^budget_'),
                CallbackQueryHandler(restart, pattern='^restart$')
            ],
            TYPE: [
                CallbackQueryHandler(type_handler, pattern='^type_'),
                CallbackQueryHandler(restart, pattern='^restart$')
            ],
            POWER: [
                CallbackQueryHandler(power_handler, pattern='^power_'),
                CallbackQueryHandler(restart, pattern='^restart$')
            ],
        },
        fallbacks=[
            CommandHandler('start', start),
            CallbackQueryHandler(restart, pattern='^restart$')
        ],
        allow_reentry=True,
        per_message=False,
        per_chat=True
    )
    return conv