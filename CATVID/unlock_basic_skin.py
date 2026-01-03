#!/usr/bin/env python
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CATVID.settings')
django.setup()

from main.models import Player, Skin, PlayerSkin
from django.utils import timezone

def unlock_basic_skin_for_all():
    """Разблокировать базовый скин для всех игроков"""
    try:
        basic_skin = Skin.objects.get(image_name='cat.png')
        players = Player.objects.all()
        
        for player in players:
            # Проверяем, есть ли уже этот скин у игрока
            player_skin, created = PlayerSkin.objects.get_or_create(
                player=player,
                skin=basic_skin,
                defaults={'unlocked_at': timezone.now()}
            )
            
            if created:
                print(f"Разблокирован базовый скин для игрока {player}")
            
            # Устанавливаем базовый скин как текущий, если у игрока нет скина
            if not player.current_skin or player.current_skin == '':
                player.current_skin = 'cat.png'
                player.save()
                print(f"Установлен базовый скин для игрока {player}")
        
        print("Базовый скин разблокирован для всех игроков!")
        
    except Skin.DoesNotExist:
        print("Базовый скин не найден! Сначала запустите create_boxes.py")

if __name__ == '__main__':
    unlock_basic_skin_for_all()