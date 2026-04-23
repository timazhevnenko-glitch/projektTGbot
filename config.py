import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("❌ Токен бота не найден!")

# Состояния для ConversationHandler
BUDGET, TYPE, POWER = range(3)

# Данные для кнопок и отображения
COUNTRY_FLAGS = {
    "Япония": "🇯🇵", "Германия": "🇩🇪", "Италия": "🇮🇹", "США": "🇺🇸", "Китай": "🇨🇳",
    "Великобритания": "🇬🇧", "Австрия": "🇦🇹", "Индия": "🇮🇳", "Франция": "🇫🇷",
    "Испания": "🇪🇸", "Швеция": "🇸🇪", "Канада": "🇨🇦",
}

MOTO_TYPES = {
    "any": {"name": "Любой тип", "emoji": "🚀"},
    "naked": {"name": "Нейкед", "emoji": "🏍️"},
    "sport": {"name": "Спортбайк", "emoji": "🏁"},
    "cruiser": {"name": "Круизер", "emoji": "🛵"},
    "enduro": {"name": "Эндуро", "emoji": "🏔️"},
}

BUDGET_RANGES = [
    {"value": 300000, "label": "до 300 000 ₽", "emoji": "💰"},
    {"value": 500000, "label": "до 500 000 ₽", "emoji": "💰"},
    {"value": 800000, "label": "до 800 000 ₽", "emoji": "💰"},
    {"value": 1200000, "label": "до 1 200 000 ₽", "emoji": "💰"},
    {"value": 2000000, "label": "до 2 000 000 ₽", "emoji": "💰"},
    {"value": 99999999, "label": "без ограничений", "emoji": "💎"},
]

POWER_RANGES = [
    {"value": 40, "label": "до 40 л.с. (A2)", "emoji": "⚡"},
    {"value": 60, "label": "до 60 л.с.", "emoji": "⚡"},
    {"value": 100, "label": "до 100 л.с.", "emoji": "⚡"},
    {"value": 150, "label": "до 150 л.с.", "emoji": "⚡"},
    {"value": 999, "label": "любая мощность", "emoji": "🔥"},
    {"value": 1000, "label": "максимальная мощь (от 150+ л.с.)", "emoji": "💪"},
]