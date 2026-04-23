import json
import logging

logger = logging.getLogger(__name__)

def load_bikes():
    try:
        with open('bikes.json', 'r', encoding='utf-8') as f:
            bikes = json.load(f)
        for bike in bikes:
            if bike.get('type') == 'neaked':   # исправление опечатки
                bike['type'] = 'naked'
        logger.info(f"✅ Загружено {len(bikes)} мотоциклов")
        return bikes
    except FileNotFoundError:
        logger.error("❌ Файл bikes.json не найден!")
        return []
    except json.JSONDecodeError:
        logger.error("❌ Ошибка парсинга bikes.json")
        return []