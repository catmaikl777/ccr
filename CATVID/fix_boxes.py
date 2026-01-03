#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CATVID.settings')
django.setup()

from main.models import Box, BoxDrop

def fix_boxes():
    """Исправляем ящики с правильными шансами"""
    
    print("Удаляем старые ящики...")
    Box.objects.all().delete()
    
    print("Создаем базовый ящик...")
    basic_box = Box.objects.create(
        name='Базовый ящик',
        description='Простой ящик с базовыми наградами',
        price=100,
        image='basic_box.svg',
        is_active=True
    )
    
    print("Создаем премиум ящик...")
    premium_box = Box.objects.create(
        name='Премиум ящик',
        description='Улучшенный ящик с редкими наградами',
        price=300,
        image='premium_box.svg',
        is_active=True
    )
    
    print("Добавляем содержимое базового ящика...")
    # Базовый ящик - общий шанс должен быть 100%
    BoxDrop.objects.create(box=basic_box, item_type='coins', item_value='50', drop_chance=40.0, is_rare=False)
    BoxDrop.objects.create(box=basic_box, item_type='clicks', item_value='100', drop_chance=30.0, is_rare=False)
    BoxDrop.objects.create(box=basic_box, item_type='skin', item_value='skin3.png', drop_chance=15.0, is_rare=False)
    BoxDrop.objects.create(box=basic_box, item_type='skin', item_value='skin4.png', drop_chance=10.0, is_rare=True)
    BoxDrop.objects.create(box=basic_box, item_type='skin', item_value='skin5.png', drop_chance=5.0, is_rare=True)
    
    print("Добавляем содержимое премиум ящика...")
    # Премиум ящик - общий шанс должен быть 100%
    BoxDrop.objects.create(box=premium_box, item_type='coins', item_value='200', drop_chance=30.0, is_rare=False)
    BoxDrop.objects.create(box=premium_box, item_type='clicks', item_value='300', drop_chance=25.0, is_rare=False)
    BoxDrop.objects.create(box=premium_box, item_type='skin', item_value='skin5.png', drop_chance=20.0, is_rare=False)
    BoxDrop.objects.create(box=premium_box, item_type='skin', item_value='skin6.png', drop_chance=15.0, is_rare=True)
    BoxDrop.objects.create(box=premium_box, item_type='skin', item_value='skin7.png', drop_chance=8.0, is_rare=True)
    BoxDrop.objects.create(box=premium_box, item_type='skin', item_value='skin8.png', drop_chance=2.0, is_rare=True)
    
    print("Проверяем созданные ящики...")
    for box in Box.objects.all():
        total_chance = sum(drop.drop_chance for drop in box.drops.all())
        print(f"- {box.name}: {box.price} монет, содержимое: {box.drops.count()} предметов, общий шанс: {total_chance}%")
        for drop in box.drops.all():
            rarity = "РЕДКИЙ" if drop.is_rare else "обычный"
            print(f"  * {drop.item_type}: {drop.item_value} ({drop.drop_chance}% - {rarity})")
    
    print("\nЯщики успешно исправлены!")

if __name__ == '__main__':
    fix_boxes()