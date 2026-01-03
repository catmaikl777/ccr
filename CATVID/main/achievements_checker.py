# achievements_checker.py
from django.db import models
from django.db.models import Count, Sum, Max
from django.utils import timezone
from django.core.cache import cache  # Используем Django cache
from datetime import timedelta
import json


class AchievementChecker:

    def __init__(self, player):
        self.player = player

    def check_all_achievements(self):
        """Проверить все достижения игрока"""
        from .models import Achievement, PlayerAchievement

        unlocked_achievements = []

        # Получаем все достижения
        achievements = Achievement.objects.all()

        for achievement in achievements:
            if not self.has_achievement(achievement):
                if self.check_achievement(achievement):
                    unlocked = self.unlock_achievement(achievement)
                    if unlocked:
                        unlocked_achievements.append(unlocked)

        return unlocked_achievements

    def has_achievement(self, achievement):
        """Проверить, есть ли у игрока достижение"""
        from .models import PlayerAchievement
        return PlayerAchievement.objects.filter(
            player=self.player,
            achievement=achievement
        ).exists()

    def check_achievement(self, achievement):
        """Проверить выполнение условий достижения"""
        from .models import BattleParticipant, Upgrade, PlayerUpgrade

        if achievement.achievement_type == 'clicks':
            return self.player.clicks >= achievement.required_clicks

        elif achievement.achievement_type == 'coins':
            return self.player.coins >= achievement.required_coins

        elif achievement.achievement_type == 'upgrades':
            # Подсчитываем улучшения игрока с уровнем > 0
            high_level_upgrades = PlayerUpgrade.objects.filter(
                player=self.player,
                level__gt=0
            ).count()
            return high_level_upgrades >= achievement.required_upgrades



        elif achievement.achievement_type == 'special':
            # Специальные достижения
            return self.check_special_achievement(achievement)

        elif achievement.achievement_type == 'collection':
            # Коллекционные достижения
            return self.check_collection_achievement(achievement)

        return False

    def check_special_achievement(self, achievement):
        """Проверить специальные достижения"""

        achievement_name = achievement.name.lower().replace(' ', '_')

        if achievement_name == 'first_click':
            return self.player.clicks >= 1
        elif achievement_name == 'millionaire':
            return self.player.coins >= 1000000
        elif achievement_name == 'click_master':
            return self.player.clicks >= 100000
        elif achievement_name == 'rich_collector':
            return self.player.coins >= 5000000

        return False

    def check_collection_achievement(self, achievement):
        """Проверить коллекционные достижения"""
        if not achievement.required_collection:
            return False

        try:
            collection_requirements = achievement.required_collection

            if isinstance(collection_requirements, dict):
                if 'skins' in collection_requirements:
                    required_skins = collection_requirements['skins']
                    # Логика подсчета скинов
                    player_skins_count = 1  # Базовый скин
                    return player_skins_count >= required_skins

            return False

        except Exception:
            return False

    def unlock_achievement(self, achievement):
        """Разблокировать достижение"""
        from .models import PlayerAchievement

        # Создаем запись о достижении
        player_achievement = PlayerAchievement.objects.create(
            player=self.player,
            achievement=achievement,
            progress_data=self.get_current_progress()
        )

        # Применяем награду
        player_achievement.apply_reward(self.player)

        return player_achievement

    def get_current_progress(self):
        """Получить текущий прогресс игрока"""
        from .models import BattleParticipant

        battles_participated = 0

        return {
            'clicks': self.player.clicks,
            'coins': self.player.coins,
            'click_power': self.player.click_power,
            'auto_clicker': self.player.auto_clicker_power,
            'critical_chance': self.player.critical_chance,
            'coin_multiplier': self.player.coin_multiplier,
            'timestamp': timezone.now().isoformat()
        }

    def get_achievement_stats(self):
        """Получить статистику по достижениям"""
        from .models import Achievement, PlayerAchievement

        total_achievements = Achievement.objects.count()
        unlocked_achievements = PlayerAchievement.objects.filter(
            player=self.player
        ).count()

        # Разбивка по типам
        by_type = {}
        for achievement_type, name in Achievement.ACHIEVEMENT_TYPES:
            if achievement_type == 'battles':
                continue
            total_type = Achievement.objects.filter(
                achievement_type=achievement_type
            ).count()
            unlocked_type = PlayerAchievement.objects.filter(
                player=self.player,
                achievement__achievement_type=achievement_type
            ).count()

            by_type[achievement_type] = {
                'unlocked': unlocked_type,
                'total': total_type,
                'percentage': (unlocked_type / total_type * 100) if total_type > 0 else 0
            }

        # Разбивка по редкости
        by_rarity = {}
        for rarity, name in Achievement.RARITY_CHOICES:
            total_rarity = Achievement.objects.filter(rarity=rarity).count()
            # Исключаем достижения батлов из статистики
            unlocked_rarity = PlayerAchievement.objects.filter(
                player=self.player,
                achievement__rarity=rarity
            ).exclude(
                achievement__achievement_type='battles'
            ).count()

            by_rarity[rarity] = {
                'unlocked': unlocked_rarity,
                'total': total_rarity,
                'percentage': (unlocked_rarity / total_rarity * 100) if total_rarity > 0 else 0
            }

        return {
            'total': total_achievements,
            'unlocked': unlocked_achievements,
            'percentage': (unlocked_achievements / total_achievements * 100)
            if total_achievements > 0 else 0,
            'by_type': by_type,
            'by_rarity': by_rarity,
            'next_achievements': self.get_next_achievements()
        }

    def get_next_achievements(self):
        """Получить ближайшие достижения к разблокировке"""
        from .models import Achievement

        next_achievements = []
        # Исключаем достижения батлов из списка ближайших
        achievements = Achievement.objects.filter(
            achievement_type__in=['clicks', 'coins']
        ).exclude(
            id__in=self.player.achievements.values_list('achievement_id', flat=True)
        ).exclude(
            achievement_type='battles'
        ).order_by('required_clicks', 'required_coins')[:5]

        for achievement in achievements:
            progress = achievement.get_progress(self.player)
            if not progress['completed']:
                next_achievements.append({
                    'achievement': achievement,
                    'progress': progress
                })

        return next_achievements