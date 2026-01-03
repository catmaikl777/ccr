from django.core.management.base import BaseCommand
from main.models import Skin
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Создает базовые скины'

    def handle(self, *args, **options):
        default_skins = [
            {
                'name': 'Кот',
                'image_name': 'cat.png',
                'description': 'Классический кот',
                'is_free': True,
                'price': 0,
                'required_clicks': 0,
                'required_coins': 0,
                'rarity': 'common',
                'order': 1
            },
            {
                'name': 'Скин 3',
                'image_name': 'skin3.png',
                'description': 'Специальный скин 3',
                'is_free': False,
                'price': 1000,
                'required_clicks': 10000,
                'required_coins': 500,
                'rarity': 'uncommon',
                'order': 2
            },
            {
                'name': 'Скин 4',
                'image_name': 'skin4.png',
                'description': 'Специальный скин 4',
                'is_free': False,
                'price': 2500,
                'required_clicks': 50000,
                'required_coins': 1500,
                'rarity': 'rare',
                'order': 3
            },
            {
                'name': 'Скин 5',
                'image_name': 'skin5.png',
                'description': 'Специальный скин 5',
                'is_free': False,
                'price': 5000,
                'required_clicks': 100000,
                'required_coins': 3000,
                'rarity': 'epic',
                'order': 4
            },
            {
                'name': 'Скин 6',
                'image_name': 'skin6.png',
                'description': 'Специальный скин 6',
                'is_free': False,
                'price': 10000,
                'required_clicks': 250000,
                'required_coins': 5000,
                'rarity': 'epic',
                'order': 5
            },
            {
                'name': 'Скин 7',
                'image_name': 'skin7.png',
                'description': 'Специальный скин 7',
                'is_free': False,
                'price': 25000,
                'required_clicks': 500000,
                'required_coins': 10000,
                'rarity': 'legendary',
                'order': 6
            },
            {
                'name': 'Скин 8',
                'image_name': 'skin8.png',
                'description': 'Специальный скин 8',
                'is_free': False,
                'price': 50000,
                'required_clicks': 1000000,
                'required_coins': 25000,
                'rarity': 'legendary',
                'order': 7
            },
        ]

        created_count = 0
        for skin_data in default_skins:
            skin, created = Skin.objects.get_or_create(
                image_name=skin_data['image_name'],
                defaults=skin_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Создан скин: {skin.name}')
            else:
                # Обновляем существующий скин
                for key, value in skin_data.items():
                    setattr(skin, key, value)
                skin.save()
                self.stdout.write(f'Обновлен скин: {skin.name}')

        self.stdout.write(self.style.SUCCESS(f'Создано/обновлено {created_count} скинов'))

        # Проверяем наличие файлов скинов
        self.check_skin_files()

    def check_skin_files(self):
        """Проверяет наличие файлов скинов на диске"""
        self.stdout.write('\nПроверка файлов скинов:')

        # Получаем путь к папке со скинами
        skins_dir = os.path.join(settings.BASE_DIR, 'main', 'static', 'main', 'skins')

        if not os.path.exists(skins_dir):
            os.makedirs(skins_dir, exist_ok=True)
            self.stdout.write(f'Создана директория: {skins_dir}')

        skins = Skin.objects.all()
        missing_files = []

        for skin in skins:
            skin_path = os.path.join(skins_dir, skin.image_name)
            if os.path.exists(skin_path):
                self.stdout.write(self.style.SUCCESS(f'✓ {skin.image_name} найден'))
            else:
                missing_files.append(skin.image_name)
                self.stdout.write(self.style.WARNING(f'✗ {skin.image_name} не найден'))

        if missing_files:
            self.stdout.write(self.style.ERROR('\nОтсутствуют файлы скинов:'))
            for filename in missing_files:
                self.stdout.write(f'  - {filename}')
            self.stdout.write(f'\nПоместите файлы в папку: {skins_dir}')