# database_optimization.py
from django.db import connection
from django.db.models import Count, Sum, Max, F
from django.core.cache import cache
import json


# Удаляем Redis, используем Django кэш или базу данных

class BattleOptimizer:

    @staticmethod
    def prefetch_battle_data(battle_id):
        """Предзагрузка данных батла"""
        from .models import Battle, BattleParticipant

        return Battle.objects.filter(id=battle_id) \
            .select_related('cache') \
            .prefetch_related(
            'participants',
            'participants__player',
            'participants__player__user'
        ).first()

    @staticmethod
    def get_battle_stats(battle_id, use_cache=True):
        """Получение статистики батла с кэшированием"""
        # Используем Django кэш вместо Redis
        cache_key = f'battle_stats_{battle_id}'

        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                return cached

        # Выполняем сложный запрос
        from .models import Battle, BattleParticipant
        from django.db.models import Sum, Count

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    b.id,
                    b.name,
                    b.status,
                    COUNT(DISTINCT bp.id) as participants_count,
                    COALESCE(SUM(bp.clicks), 0) as total_clicks,
                    COALESCE(MAX(bp.clicks), 0) as top_score,
                    (
                        SELECT bp2.player_id 
                        FROM main_battleparticipant bp2 
                        WHERE bp2.battle_id = b.id 
                        ORDER BY bp2.clicks DESC 
                        LIMIT 1
                    ) as top_player_id
                FROM main_battle b
                LEFT JOIN main_battleparticipant bp ON bp.battle_id = b.id
                WHERE b.id = %s
                GROUP BY b.id
            """, [battle_id])

            columns = [col[0] for col in cursor.description]
            stats = dict(zip(columns, cursor.fetchone()))

        # Кэшируем на 5 секунд (в Django кэше)
        cache.set(cache_key, stats, 5)

        return stats

    @staticmethod
    def update_battle_cache(battle_id):
        """Обновление кэша батла"""
        from .models import Battle, BattleParticipant, BattleCache
        from django.utils import timezone

        battle = Battle.objects.get(id=battle_id)

        # Получаем топ-50 участников
        top_participants = BattleParticipant.objects.filter(battle=battle) \
                               .select_related('player', 'player__user') \
                               .order_by('-clicks')[:50] \
            .values('id', 'player_id', 'clicks', 'coins_earned', 'player__user__username')

        # Общая статистика
        total_stats = BattleParticipant.objects.filter(battle=battle) \
            .aggregate(
            total_clicks=Sum('clicks'),
            total_players=Count('id'),
            avg_clicks=Sum('clicks') / Count('id')
        )

        cache_data = {
            'top_participants': list(top_participants),
            'stats': total_stats,
            'updated_at': timezone.now().isoformat()
        }

        # Сохраняем в Django кэш
        cache_key = f'battle_cache_{battle_id}'
        cache.set(cache_key, cache_data, 10)

        # Сохраняем в PostgreSQL
        BattleCache.objects.update_or_create(
            battle=battle,
            defaults={
                'participants_json': cache_data['top_participants'],
                'stats_json': cache_data['stats'],
                'expires_at': timezone.now() + timezone.timedelta(seconds=10)
            }
        )