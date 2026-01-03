#!/usr/bin/env python
"""
Скрипт для создания базовых скинов в игре
Запуск: python manage.py shell < create_skins.py
"""

import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CATVID.settings')
django.setup()

from main.models import Skin

def create_basic_skins():
    """Создает базовые скины для игры"""
    
    skins_data = [
        {
            'name': 'Базовый котик',
            'image_name': 'cat.png',
            'description': 'Стандартный милый котик для начинающих игроков',
            'is_free': True,
            'price': 0,
            'required_clicks': 0,
            'required_coins': 0,
            'rarity': 'common',
            'order': 1
        },
        {
            'name': 'Космический котик',
            'image_name': 'skin3.png',
            'description': 'Котик-космонавт для покорения вселенной кликов!',
            'is_free': False,
            'price': 100,
            'required_clicks': 50,
            'required_coins': 100,
            'rarity': 'uncommon',
            'order': 2
        },
        {
            'name': 'Пиратский котик',
            'image_name': 'skin4.png',
            'description': 'Отважный котик-пират в поисках сокровищ',
            'is_free': False,
            'price': 250,
            'required_clicks': 200,
            'required_coins': 250,
            'rarity': 'uncommon',
            'order': 3
        },
        {
            'name': 'Рыцарский котик',
            'image_name': 'skin5.png',
            'description': 'Благородный котик-рыцарь в сверкающих доспехах',
            'is_free': False,
            'price': 500,
            'required_clicks': 500,
            'required_coins': 500,
            'rarity': 'rare',
            'order': 4
        },
        {
            'name': 'Магический котик',
            'image_name': 'skin6.png',
            'description': 'Волшебный котик с мистическими способностями',
            'is_free': False,
            'price': 1000,
            'required_clicks': 1000,
            'required_coins': 1000,
            'rarity': 'rare',
            'order': 5
        },
        {
            'name': 'Королевский котик',
            'image_name': 'skin7.png',
            'description': 'Величественный котик в королевской мантии',
            'is_free': False,
            'price': 2000,
            'required_clicks': 2500,
            'required_coins': 2000,
            'rarity': 'epic',
            'order': 6
        },
        {
            'name': 'Легендарный котик',
            'image_name': 'skin8.png',
            'description': 'Редчайший котик с невероятной силой кликов!',
            'is_free': False,
            'price': 5000,
            'required_clicks': 10000,
            'required_coins': 5000,
            'rarity': 'legendary',
            'order': 7
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for skin_data in skins_data:
        skin, created = Skin.objects.get_or_create(
            image_name=skin_data['image_name'],
            defaults=skin_data
        )
        
        if created:
            created_count += 1
            print(f"✅ Создан скин: {skin.name}")
        else:
            # Обновляем существующий скин
            for key, value in skin_data.items():
                if key != 'image_name':  # Не обновляем ключевое поле
                    setattr(skin, key, value)
            skin.save()
            updated_count += 1
            print(f"🔄 Обновлен скин: {skin.name}")
    
    print(f"\n📊 Итого:")
    print(f"   Создано новых скинов: {created_count}")
    print(f"   Обновлено скинов: {updated_count}")
    print(f"   Всего скинов в базе: {Skin.objects.count()}")
    
    # Показываем все скины
    print(f"\n📋 Все скины в базе данных:")
    for skin in Skin.objects.all().order_by('order'):
        status = "🆓" if skin.is_free else f"💰{skin.price}"
        rarity_emoji = {
            'common': '⚪',
            'uncommon': '🟢', 
            'rare': '🔵',
            'epic': '🟣',
            'legendary': '🟠'
        }.get(skin.rarity, '⚪')
        
        print(f"   {rarity_emoji} {skin.name} ({skin.image_name}) - {status}")

if __name__ == '__main__':
    print("🎮 Создание базовых скинов для игры...")
    create_basic_skins()
    print("✨ Готово!")