#!/usr/bin/env python
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CATVID.settings')
django.setup()

from main.models import Box, BoxDrop, Skin

def update_box_data():
    # Удаляем старые данные
    BoxDrop.objects.all().delete()
    Box.objects.all().delete()
    
    # Создаем скины если их нет
    skins_data = [
        {'name': 'Базовый кот', 'image_name': 'cat.png', 'rarity': 'common'},
        {'name': 'Кот-ниндзя', 'image_name': 'skin3.png', 'rarity': 'common'},
        {'name': 'Космический кот', 'image_name': 'skin4.png', 'rarity': 'uncommon'},
        {'name': 'Пиратский кот', 'image_name': 'skin5.png', 'rarity': 'uncommon'},
        {'name': 'Королевский кот', 'image_name': 'skin6.png', 'rarity': 'rare'},
        {'name': 'Магический кот', 'image_name': 'skin7.png', 'rarity': 'rare'},
        {'name': 'Легендарный кот', 'image_name': 'skin8.png', 'rarity': 'legendary'},
    ]
    
    for skin_data in skins_data:
        skin, created = Skin.objects.get_or_create(
            image_name=skin_data['image_name'],
            defaults={
                'name': skin_data['name'],
                'description': f"Красивый скин: {skin_data['name']}",
                'is_free': False,
                'price': 0,
                'rarity': skin_data['rarity']
            }
        )
        if created:
            print(f"Создан скин: {skin.name}")
    
    # Создаем ящики с правильными значениями drop_chance
    # Обычный ящик
    basic_box = Box.objects.create(
        name="Обычный ящик",
        description='Содержит обычные скины, монеты и клики',
        price=100,
        image='basic_box.png'
    )
    print(f"Создан ящик: {basic_box.name}")
    
    # Добавляем содержимое обычного ящика (значения в процентах как десятичные дроби)
    BoxDrop.objects.create(box=basic_box, item_type='coins', item_value='50', drop_chance=40, is_rare=False)
    BoxDrop.objects.create(box=basic_box, item_type='clicks', item_value='100', drop_chance=30, is_rare=False)
    BoxDrop.objects.create(box=basic_box, item_type='skin', item_value='skin3.png', drop_chance=15, is_rare=False)
    BoxDrop.objects.create(box=basic_box, item_type='skin', item_value='skin4.png', drop_chance=10, is_rare=False)
    BoxDrop.objects.create(box=basic_box, item_type='skin', item_value='skin5.png', drop_chance=5, is_rare=True)
    
    # Премиум ящик
    premium_box = Box.objects.create(
        name="Премиум ящик",
        description='Содержит редкие скины и больше наград',
        price=300,
        image='premium_box.png'
    )
    print(f"Создан ящик: {premium_box.name}")
    
    # Добавляем содержимое премиум ящика
    BoxDrop.objects.create(box=premium_box, item_type='coins', item_value='200', drop_chance=30, is_rare=False)
    BoxDrop.objects.create(box=premium_box, item_type='clicks', item_value='300', drop_chance=25, is_rare=False)
    BoxDrop.objects.create(box=premium_box, item_type='skin', item_value='skin5.png', drop_chance=20, is_rare=False)
    BoxDrop.objects.create(box=premium_box, item_type='skin', item_value='skin6.png', drop_chance=15, is_rare=True)
    BoxDrop.objects.create(box=premium_box, item_type='skin', item_value='skin7.png', drop_chance=8, is_rare=True)
    BoxDrop.objects.create(box=premium_box, item_type='skin', item_value='skin8.png', drop_chance=2, is_rare=True)
    
    print("Данные ящиков обновлены!")

if __name__ == '__main__':
    update_box_data()