# monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Метрики Prometheus
BATTLE_CLICKS_TOTAL = Counter('battle_clicks_total', 'Total battle clicks')
BATTLE_ACTIVE_PLAYERS = Gauge('battle_active_players', 'Active players in battles')
BATTLE_RESPONSE_TIME = Histogram('battle_response_time', 'Battle API response time')


# Декоратор для мониторинга
def monitor_battle_request(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()

        # Инкрементируем счетчик активных игроков
        BATTLE_ACTIVE_PLAYERS.inc()

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Уменьшаем счетчик
            BATTLE_ACTIVE_PLAYERS.dec()

            # Замеряем время ответа
            duration = time.time() - start_time
            BATTLE_RESPONSE_TIME.observe(duration)

    return wrapper


# Автоматическое масштабирование
class BattleAutoScaler:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=3)

    def check_load(self):
        """Проверка нагрузки и масштабирование"""
        # Получаем текущую нагрузку
        active_battles = self.redis.get('active_battles_count') or 0
        active_players = self.redis.get('active_players_count') or 0
        click_rate = self.redis.get('click_rate_per_second') or 0

        # Логика масштабирования
        if int(active_players) > 1000:
            self.scale_up()
        elif int(active_players) < 100:
            self.scale_down()

    def scale_up(self):
        """Увеличение мощности"""
        # Здесь логика для горизонтального масштабирования
        # Например, запуск дополнительных инстансов
        pass

    def scale_down(self):
        """Уменьшение мощности"""
        pass