#!/usr/bin/env python
"""
Скрипт для создания базовых ящиков со скинами
Запуск: python manage.py shell < create_boxes.py
"""

import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CATVID.settings')
django.setup()

from main.models import Box, BoxDrop

def create_basic_boxes():
    """Создает базовые ящики для игры"""
    
    # Сначала создаем ящики
    boxes_data = [
        {
            'name': 'Базовый ящик',
            'description': 'Простой ящик с базовыми наградами для начинающих',
            'price': 50,
            'image': 'basic_box.svg',
            'is_active': True
        },
        {
            'name': 'Премиум ящик',
            'description': 'Улучшенный ящик с редкими скинами и большими наградами',
            'price': 200,
            'image': 'premium_box.svg',
            'is_active': True
        }
    ]
    
    created_boxes = 0
    
    for box_data in boxes_data:
        box, created = Box.objects.get_or_create(
            name=box_data['name'],
            defaults=box_data
        )
        
        if created:
            created_boxes += 1
            print(f"✅ Создан ящик: {box.name}")
        else:
            # Обновляем существующий ящик
            for key, value in box_data.items():
                if key != 'name':
                    setattr(box, key, value)
            box.save()
            print(f"🔄 Обновлен ящик: {box.name}")
    
    # Теперь создаем содержимое ящиков
    create_box_drops()
    
    print(f"\n📊 Итого:")
    print(f"   Создано ящиков: {created_boxes}")
    print(f"   Всего ящиков в базе: {Box.objects.count()}")

def create_box_drops():
    """Создает содержимое для ящиков"""
    
    # Получаем ящики
    basic_box = Box.objects.get(name='Базовый ящик')
    premium_box = Box.objects.get(name='Премиум ящик')
    
    # Очищаем старые дропы
    BoxDrop.objects.filter(box__in=[basic_box, premium_box]).delete()
    
    # Содержимое базового ящика
    basic_drops = [
        {
            'box': basic_box,
            'item_type': 'coins',
            'item_value': '25',
            'drop_chance': 40.0,
            'is_rare': False
        },
        {
            'box': basic_box,
            'item_type': 'coins',
            'item_value': '50',
            'drop_chance': 25.0,
            'is_rare': False
        },
        {
            'box': basic_box,
            'item_type': 'clicks',
            'item_value': '10',
            'drop_chance': 20.0,
            'is_rare': False
        },
        {
            'box': basic_box,
            'item_type': 'skin',
            'item_value': 'skin3.png',
            'drop_chance': 10.0,
            'is_rare': True
        },
        {
            'box': basic_box,
            'item_type': 'skin',
            'item_value': 'skin4.png',
            'drop_chance': 5.0,
            'is_rare': True
        }
    ]
    
    # Содержимое премиум ящика
    premium_drops = [
        {
            'box': premium_box,
            'item_type': 'coins',
            'item_value': '100',
            'drop_chance': 30.0,
            'is_rare': False
        },
        {
            'box': premium_box,
            'item_type': 'coins',
            'item_value': '200',
            'drop_chance': 20.0,
            'is_rare': False
        },
        {
            'box': premium_box,
            'item_type': 'clicks',
            'item_value': '50',
            'drop_chance': 15.0,
            'is_rare': False
        },
        {
            'box': premium_box,
            'item_type': 'skin',
            'item_value': 'skin5.png',
            'drop_chance': 15.0,
            'is_rare': True
        },
        {
            'box': premium_box,
            'item_type': 'skin',
            'item_value': 'skin6.png',
            'drop_chance': 10.0,
            'is_rare': True
        },
        {
            'box': premium_box,
            'item_type': 'skin',
            'item_value': 'skin7.png',
            'drop_chance': 7.0,
            'is_rare': True
        },
        {
            'box': premium_box,
            'item_type': 'skin',
            'item_value': 'skin8.png',
            'drop_chance': 3.0,
            'is_rare': True
        }
    ]
    
    # Создаем дропы
    all_drops = basic_drops + premium_drops
    created_drops = 0
    
    for drop_data in all_drops:
        drop = BoxDrop.objects.create(**drop_data)
        created_drops += 1
        
        rarity_text = "🌟 Редкий" if drop.is_rare else "Обычный"
        print(f"   📦 {drop.box.name}: {drop.item_type} {drop.item_value} ({drop.drop_chance}%) - {rarity_text}")
    
    print(f"\n📋 Создано дропов: {created_drops}")

def show_boxes_summary():
    """Показывает сводку по всем ящикам"""
    print(f"\n📋 Сводка по ящикам:")
    
    for box in Box.objects.all():
        print(f"\n🎁 {box.name} - {box.price} монет")
        print(f"   {box.description}")
        
        drops = box.drops.all().order_by('-is_rare', '-drop_chance')
        total_chance = sum(drop.drop_chance for drop in drops)
        
        print(f"   📊 Содержимое (общий шанс: {total_chance}%):")
        for drop in drops:
            rarity_emoji = "🌟" if drop.is_rare else "📦"
            item_name = drop.item_value
            if drop.item_type == 'skin':
                item_name = f"Скин {drop.item_value}"
            elif drop.item_type == 'coins':
                item_name = f"{drop.item_value} монет"
            elif drop.item_type == 'clicks':
                item_name = f"{drop.item_value} кликов"
            
            print(f"      {rarity_emoji} {item_name} - {drop.drop_chance}%")

if __name__ == '__main__':
    print("🎁 Создание базовых ящиков для игры...")
    create_basic_boxes()
    show_boxes_summary()
    print("✨ Готово!")