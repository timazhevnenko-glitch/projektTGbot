import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import BUDGET, TYPE, POWER, BUDGET_RANGES, POWER_RANGES, MOTO_TYPES, COUNTRY_FLAGS
from keyboards import Keyboards
from database import load_bikes

logger = logging.getLogger(__name__)
BIKES = load_bikes()

# Нижние границы мощности
LOWER_POWER_LIMITS = {
    40: 0,
    60: 35,
    100: 60,
    150: 100,
    999: 0,
    1000: 130  # максимальная мощь - от 130 л.с и выше
}

# -------------------------------------------------------------------
# Reply-клавиатура (всегда под полем ввода)
# -------------------------------------------------------------------
def get_main_keyboard():
    # Клавиатура удалена - используйте меню команд бота
    return None

# -------------------------------------------------------------------
# Вспомогательная функция показа результатов
# -------------------------------------------------------------------
async def show_results(query, context: ContextTypes.DEFAULT_TYPE, page: int):
    bikes = context.user_data.get('filtered', [])
    total = len(bikes)
    per_page = 5
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = min(start + per_page, total)

    budget_label = next(b['label'] for b in BUDGET_RANGES if b['value'] == context.user_data['budget'])
    power_label = next(p['label'] for p in POWER_RANGES if p['value'] == context.user_data['power'])
    
    # Обработка "любого типа"
    moto_type = context.user_data['type']
    if moto_type == 'any':
        type_info = {"name": "Любой тип", "emoji": "🏍️"}
    else:
        type_info = MOTO_TYPES.get(moto_type, {"name": "Любой", "emoji": "🏍️"})

    text = f"🎉 <b>Результаты</b>\n\n💰 {budget_label}\n🏍️ {type_info['name']}\n⚡ {power_label}\n\n"
    text += f"<i>Найдено: {total}</i> | <i>Стр. {page}/{pages}</i>\n\n"

    for i, bike in enumerate(bikes[start:end], start=start + 1):
        name = bike.get('name', '?')
        price = bike.get('price', 0)
        power_val = bike.get('power', 0)
        year = bike.get('year', '?')
        country = bike.get('country', '')
        flag = COUNTRY_FLAGS.get(country, '🌍')
        text += f"<b>{i}. {name}</b>\n└ 💰 {price:,} ₽ | ⚡ {power_val} л.с.\n└ 📅 {year} | {flag} {country}\n\n"

    context.user_data['page'] = page
    await query.edit_message_text(text, parse_mode='HTML', reply_markup=Keyboards.results(page, pages))

# -------------------------------------------------------------------
# Функция пересчёта результатов
# -------------------------------------------------------------------
async def refresh_results(query, context: ContextTypes.DEFAULT_TYPE):
    budget = context.user_data.get('budget')
    moto_type = context.user_data.get('type')
    power = context.user_data.get('power')
    
    if None in (budget, moto_type, power):
        await query.edit_message_text(
            "✏️ <b>Выберите параметр:</b>",
            parse_mode='HTML', reply_markup=Keyboards.edit_params()
        )
        return

    lower = LOWER_POWER_LIMITS.get(power, 0)
    
    # Определяем верхний предел мощности
    if power == 1000:  # максимальная мощь
        upper = 999999
    else:
        upper = power
    
    # Если выбран "любой тип", не фильтруем по типу
    if moto_type == 'any':
        filtered = [b for b in BIKES
                    if b.get('price', 0) <= budget
                    and lower <= b.get('power', 0) <= upper]
    else:
        filtered = [b for b in BIKES
                    if b.get('price', 0) <= budget
                    and b.get('type') == moto_type
                    and lower <= b.get('power', 0) <= upper]
    
    filtered.sort(key=lambda x: (-x['power'], x['price']))
    context.user_data['filtered'] = filtered

    if not filtered:
        await query.edit_message_text(
            "😕 <b>Ничего не найдено</b>\n\nПопробуйте расширить параметры.",
            parse_mode='HTML', reply_markup=Keyboards.edit_params()
        )
        return

    context.user_data['total'] = len(filtered)
    context.user_data['page'] = 1
    await show_results(query, context, 1)

# -------------------------------------------------------------------
# Обработчики диалога (основной поток)
# -------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "🏍️ <b>Добро пожаловать в MotoBot!</b>\n\n"
        "Я помогу подобрать идеальный мотоцикл.\n"
        "Выберите способ подбора:",
        parse_mode='HTML',
        reply_markup=Keyboards.start_mode()
    )
    return -1  # Временное состояние для выбора режима

async def handle_mode_step_by_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает пошаговый выбор"""
    query = update.callback_query
    await query.answer()
    context.user_data['selection_mode'] = 'step_by_step'
    
    await query.edit_message_text(
        "<i>Начнем с выбора бюджета</i>",
        parse_mode='HTML'
    )
    await query.message.reply_text(
        "💰 Выберите бюджет:",
        reply_markup=Keyboards.budget()
    )
    return BUDGET

async def handle_mode_custom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает выбор в произвольном порядке"""
    query = update.callback_query
    await query.answer()
    context.user_data['selection_mode'] = 'custom'
    
    await query.edit_message_text(
        "✏️ <b>Выберите параметры в любом порядке:</b>",
        parse_mode='HTML',
        reply_markup=Keyboards.edit_params()
    )
    return -1  # Не в основном диалоге

async def budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['budget'] = int(query.data.split('_')[1])
    selected = next(b for b in BUDGET_RANGES if b['value'] == context.user_data['budget'])
    
    # Проверяем режим выбора
    if context.user_data.get('selection_mode') == 'custom':
        # Если произвольный режим, показываем меню
        await query.edit_message_text(
            f"✅ <b>Бюджет:</b> {selected['emoji']} {selected['label']}",
            parse_mode='HTML'
        )
        await query.message.reply_text(
            "✏️ <b>Выберите следующий параметр:</b>",
            reply_markup=Keyboards.edit_params()
        )
        return -1
    else:
        # Пошаговый режим - продолжаем диалог
        await query.edit_message_text(
            f"✅ <b>Бюджет:</b> {selected['emoji']} {selected['label']}\n\nВыберите тип:",
            parse_mode='HTML', reply_markup=Keyboards.moto_type()
        )
        return TYPE

async def budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['budget'] = int(query.data.split('_')[1])
    selected = next(b for b in BUDGET_RANGES if b['value'] == context.user_data['budget'])
    await query.edit_message_text(
        f"✅ <b>Бюджет:</b> {selected['emoji']} {selected['label']}\n\nВыберите тип:",
        parse_mode='HTML', reply_markup=Keyboards.moto_type()
    )
    return TYPE

async def type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['type'] = query.data.split('_')[1]
    type_info = MOTO_TYPES[context.user_data['type']]
    
    if context.user_data.get('selection_mode') == 'custom':
        await query.edit_message_text(
            f"✅ <b>Тип:</b> {type_info['emoji']} {type_info['name']}",
            parse_mode='HTML'
        )
        await query.message.reply_text(
            "✏️ <b>Выберите следующий параметр:</b>",
            reply_markup=Keyboards.edit_params()
        )
        return -1
    else:
        budget_val = context.user_data['budget']
        budget_label = next(b['label'] for b in BUDGET_RANGES if b['value'] == budget_val)
        await query.edit_message_text(
            f"✅ <b>Бюджет:</b> {budget_label}\n"
            f"✅ <b>Тип:</b> {type_info['emoji']} {type_info['name']}\n\nВыберите мощность:",
            parse_mode='HTML', reply_markup=Keyboards.power()
        )
        return POWER

async def power_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['power'] = int(query.data.split('_')[1])
    
    if context.user_data.get('selection_mode') == 'custom':
        power_info = next(p for p in POWER_RANGES if p['value'] == context.user_data['power'])
        await query.edit_message_text(
            f"✅ <b>Мощность:</b> {power_info['emoji']} {power_info['label']}",
            parse_mode='HTML'
        )
        await refresh_results(query, context)
        return -1
    else:
        await refresh_results(query, context)
        return ConversationHandler.END

# -------------------------------------------------------------------
# Вспомогательная функция для проверки завершенности настройки
# -------------------------------------------------------------------
def is_setup_complete(user_data):
    return all(user_data.get(key) is not None for key in ['budget', 'type', 'power'])

# -------------------------------------------------------------------
# Обработчики для изменения параметров (после диалога)
# -------------------------------------------------------------------
async def handle_budget_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['budget'] = int(query.data.split('_')[1])
    
    # Если все параметры выбраны, показываем результаты
    if is_setup_complete(context.user_data):
        await refresh_results(query, context)
    else:
        # Иначе продолжаем диалог
        await query.edit_message_text("✏️ <b>Выберите параметр:</b>", parse_mode='HTML', reply_markup=Keyboards.edit_params())

async def handle_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['type'] = query.data.split('_')[1]
    
    if is_setup_complete(context.user_data):
        await refresh_results(query, context)
    else:
        await query.edit_message_text("✏️ <b>Выберите параметр:</b>", parse_mode='HTML', reply_markup=Keyboards.edit_params())

async def handle_power_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['power'] = int(query.data.split('_')[1])
    
    if is_setup_complete(context.user_data):
        await refresh_results(query, context)
    else:
        await query.edit_message_text("✏️ <b>Выберите параметр:</b>", parse_mode='HTML', reply_markup=Keyboards.edit_params())

# -------------------------------------------------------------------
# Обработчики пагинации и редактирования
# -------------------------------------------------------------------
async def pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split('_')[1])
    await show_results(query, context, page)

async def edit_params(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✏️ <b>Выберите параметр:</b>", parse_mode='HTML', reply_markup=Keyboards.edit_params())

async def edit_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    current = context.user_data.get('budget')
    await query.edit_message_text("💰 <b>Выберите бюджет:</b>", parse_mode='HTML',
                                  reply_markup=Keyboards.budget(current))

async def edit_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    current = context.user_data.get('type')
    await query.edit_message_text("🏍️ <b>Выберите тип:</b>", parse_mode='HTML',
                                  reply_markup=Keyboards.moto_type(current))

async def edit_power(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    current = context.user_data.get('power')
    await query.edit_message_text("⚡ <b>Выберите мощность:</b>", parse_mode='HTML',
                                  reply_markup=Keyboards.power(current))

async def back_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✏️ <b>Редактирование:</b>", parse_mode='HTML', reply_markup=Keyboards.edit_params())

async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if 'filtered' in context.user_data:
        await show_results(query, context, context.user_data.get('page', 1))
    else:
        await query.edit_message_text("❌ Нет активных результатов. Используйте /start", reply_markup=None)

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Перезапуск из inline кнопки"""
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text(
        "🏍️ <b>Добро пожаловать в MotoBot!</b>\n\n"
        "Я помогу подобрать идеальный мотоцикл.\n"
        "Выберите способ подбора:",
        parse_mode='HTML',
        reply_markup=Keyboards.start_mode()
    )
    return -1

async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Перезапуск из команды /restart"""
    context.user_data.clear()
    await update.message.reply_text(
        "🏍️ <b>Добро пожаловать в MotoBot!</b>\n\n"
        "Я помогу подобрать идеальный мотоцикл.\n"
        "Выберите способ подбора:",
        parse_mode='HTML',
        reply_markup=Keyboards.start_mode()
    )
    return -1

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ <b>Помощь</b>\n\n"
        "/start - найти мотоцикл\n"
        "/restart - перезапуск\n"
        "/help - помощь\n\n"
        "1️⃣ Выберите бюджет\n"
        "2️⃣ Выберите тип\n"
        "3️⃣ Выберите мощность\n"
        "4️⃣ Получите варианты",
        parse_mode='HTML'
    )

# -------------------------------------------------------------------
# Обработчик текстовых кнопок (reply-клавиатура)
# -------------------------------------------------------------------
async def handle_main_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Reply-клавиатуры удалены - используйте меню команд бота
    pass