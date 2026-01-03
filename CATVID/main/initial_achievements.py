# initial_achievements.py
from django.core.management.base import BaseCommand
from main.models import Achievement


class Command(BaseCommand):
    help = 'Создать начальные достижения'

    def handle(self, *args, **kwargs):
        achievements = [
            # Базовые достижения
            {
                'name': 'Первый клик',
                'description': 'Сделайте ваш первый клик',
                'achievement_type': 'clicks',
                'rarity': 'common',
                'icon': 'fas fa-mouse-pointer',
                'required_clicks': 1,
                'reward_coins': 10,
                'badge_color': '#808080',
                'order': 1
            },
            {
                'name': '100 кликов',
                'description': 'Сделайте 100 кликов',
                'achievement_type': 'clicks',
                'rarity': 'common',
                'icon': 'fas fa-mouse',
                'required_clicks': 100,
                'reward_coins': 100,
                'reward_click_power': 1,
                'badge_color': '#808080',
                'order': 2
            },
            {
                'name': '1000 кликов',
                'description': 'Сделайте 1000 кликов',
                'achievement_type': 'clicks',
                'rarity': 'uncommon',
                'icon': 'fas fa-hand-pointer',
                'required_clicks': 1000,
                'reward_coins': 500,
                'reward_click_power': 2,
                'badge_color': '#1EFF00',
                'order': 3
            },
            # Монетные достижения
            {
                'name': 'Первые монеты',
                'description': 'Заработайте 100 монет',
                'achievement_type': 'coins',
                'rarity': 'common',
                'icon': 'fas fa-coins',
                'required_coins': 100,
                'reward_coins': 50,
                'badge_color': '#808080',
                'order': 10
            },
            {
                'name': 'Тысячник',
                'description': 'Накопите 1000 монет',
                'achievement_type': 'coins',
                'rarity': 'common',
                'icon': 'fas fa-money-bill-wave',
                'required_coins': 1000,
                'reward_coins': 200,
                'reward_coin_multiplier': 0.1,
                'badge_color': '#808080',
                'order': 11
            },
            {
                'name': 'Миллионер',
                'description': 'Накопите 1,000,000 монет',
                'achievement_type': 'coins',
                'rarity': 'legendary',
                'icon': 'fas fa-crown',
                'required_coins': 1000000,
                'reward_coins': 50000,
                'reward_coin_multiplier': 0.5,
                'unlock_skin': 'skin_gold.png',
                'badge_color': '#FF8000',
                'order': 12
            },
            # Улучшения
            {
                'name': 'Первое улучшение',
                'description': 'Купите первое улучшение',
                'achievement_type': 'upgrades',
                'rarity': 'common',
                'icon': 'fas fa-arrow-up',
                'required_upgrades': 1,
                'reward_coins': 100,
                'badge_color': '#808080',
                'order': 20
            },
            {
                'name': 'Улучшатель',
                'description': 'Купите 10 улучшений',
                'achievement_type': 'upgrades',
                'rarity': 'uncommon',
                'icon': 'fas fa-chart-line',
                'required_upgrades': 10,
                'reward_coins': 500,
                'reward_critical_chance': 1,
                'badge_color': '#1EFF00',
                'order': 21
            },
            {
                'name': 'Мастер улучшений',
                'description': 'Купите все улучшения',
                'achievement_type': 'upgrades',
                'rarity': 'epic',
                'icon': 'fas fa-tools',
                'required_upgrades': 20,
                'reward_coins': 10000,
                'reward_click_power': 10,
                'reward_auto_clicker': 5,
                'badge_color': '#A335EE',
                'order': 22
            },
            # Батлы
            {
                'name': 'Первый бой',
                'description': 'Примите участие в первом батле',
                'achievement_type': 'battles',
                'rarity': 'common',
                'icon': 'fas fa-fist-raised',
                'required_battles': 1,
                'reward_coins': 200,
                'badge_color': '#808080',
                'order': 30
            },
            {
                'name': 'Ветеран',
                'description': 'Участвуйте в 10 батлах',
                'achievement_type': 'battles',
                'rarity': 'uncommon',
                'icon': 'fas fa-shield-alt',
                'required_battles': 10,
                'reward_coins': 1000,
                'badge_color': '#1EFF00',
                'order': 31
            },
            {
                'name': 'Победитель',
                'description': 'Выиграйте 5 батлов',
                'achievement_type': 'battles',
                'rarity': 'rare',
                'icon': 'fas fa-trophy',
                'required_wins': 5,
                'reward_coins': 5000,
                'reward_click_power': 5,
                'unlock_skin': 'skin_warrior.png',
                'badge_color': '#0070DD',
                'order': 32
            },
            # Специальные
            {
                'name': 'Спидкликер',
                'description': 'Сделайте 10 кликов за 1 секунду',
                'achievement_type': 'special',
                'rarity': 'rare',
                'icon': 'fas fa-bolt',
                'reward_coins': 1000,
                'reward_click_power': 3,
                'badge_color': '#0070DD',
                'is_secret': True,
                'secret_description': 'Разблокируйте, чтобы увидеть',
                'order': 40
            },
        ]

        created_count = 0
        for achievement_data in achievements:
            achievement, created = Achievement.objects.update_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Создано {created_count} достижений')
        )