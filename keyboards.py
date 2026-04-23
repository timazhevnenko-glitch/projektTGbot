from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import BUDGET_RANGES, MOTO_TYPES, POWER_RANGES

class Keyboards:
    @staticmethod
    def start_mode():
        """Меню выбора способа подбора"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 Пошаговый выбор", callback_data="mode_step_by_step")],
            [InlineKeyboardButton("🔧 По своей последовательности", callback_data="mode_custom")]
        ])

    @staticmethod
    def budget(current=None):
        buttons = []
        row = []
        for i, b in enumerate(BUDGET_RANGES):
            prefix = "✅ " if current == b["value"] else b["emoji"]
            row.append(InlineKeyboardButton(f"{prefix} {b['label']}", callback_data=f"budget_{b['value']}"))
            if (i + 1) % 2 == 0 or i == len(BUDGET_RANGES) - 1:
                buttons.append(row)
                row = []
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_edit")])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def moto_type(current=None):
        buttons = []
        row = []
        for i, (key, info) in enumerate(MOTO_TYPES.items()):
            prefix = "✅ " if current == key else info["emoji"]
            row.append(InlineKeyboardButton(f"{prefix} {info['name']}", callback_data=f"type_{key}"))
            if (i + 1) % 2 == 0 or i == len(MOTO_TYPES) - 1:
                buttons.append(row)
                row = []
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_edit")])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def power(current=None):
        buttons = []
        row = []
        for i, p in enumerate(POWER_RANGES):
            prefix = "✅ " if current == p["value"] else p["emoji"]
            row.append(InlineKeyboardButton(f"{prefix} {p['label']}", callback_data=f"power_{p['value']}"))
            if (i + 1) % 2 == 0 or i == len(POWER_RANGES) - 1:
                buttons.append(row)
                row = []
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_edit")])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def results(page, total_pages):
        buttons = []
        nav = []
        if page > 1:
            nav.append(InlineKeyboardButton("◀️ Назад", callback_data=f"page_{page-1}"))
        if page < total_pages:
            nav.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"page_{page+1}"))
        if nav:
            buttons.append(nav)
        buttons.append([
            InlineKeyboardButton("🔄 Начать заново", callback_data="restart"),
            InlineKeyboardButton("⬅️ Изменить параметры", callback_data="edit_params")
        ])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def edit_params():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Изменить бюджет", callback_data="edit_budget")],
            [InlineKeyboardButton("🏍️ Изменить тип", callback_data="edit_type")],
            [InlineKeyboardButton("⚡ Изменить мощность", callback_data="edit_power")],
            [InlineKeyboardButton("🔄 Полный перезапуск", callback_data="restart")],
            [InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")]
        ])