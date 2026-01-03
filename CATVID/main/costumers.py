# consumers.py
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache  # Заменяем Redis на Django cache


class BattleConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.battle_id = None
        self.player_id = None
        self.room_group_name = None

    async def connect(self):
        self.battle_id = self.scope['url_route']['kwargs']['battle_id']
        self.player_id = self.scope['user'].id if self.scope['user'].is_authenticated else 'anonymous'
        self.room_group_name = f'battle_{self.battle_id}'

        # Присоединяемся к комнате
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Отправляем начальные данные
        await self.send_initial_data()

    async def disconnect(self, close_code):
        # Покидаем комнату
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'click':
            await self.handle_click(data)
        elif action == 'join':
            await self.handle_join(data)
        elif action == 'leave':
            await self.handle_leave(data)
        elif action == 'ping':
            await self.send(json.dumps({'action': 'pong'}))

    async def handle_click(self, data):
        # Используем Django cache для быстрой обработки кликов
        timestamp = data.get('timestamp')
        clicks = data.get('clicks', 1)

        # Сохраняем в cache
        cache_key = f'battle:{self.battle_id}:player:{self.player_id}:clicks'
        current_clicks = cache.get(cache_key, 0)
        cache.set(cache_key, current_clicks + clicks, 60)

        # Отправляем обновление всем участникам
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'click_update',
                'player_id': self.player_id,
                'clicks': clicks,
                'timestamp': timestamp
            }
        )

        # Асинхронно сохраняем в базу
        asyncio.create_task(self.save_click_to_db(data))

    @database_sync_to_async
    def save_click_to_db(self, data):
        from .models import Battle, BattleParticipant, BattleClick
        from .database_optimization import BattleOptimizer

        try:
            battle = Battle.objects.get(id=self.battle_id)
            participant, created = BattleParticipant.objects.get_or_create(
                battle=battle,
                player_id=self.player_id if self.player_id != 'anonymous' else None
            )

            participant.clicks += data.get('clicks', 1)
            participant.save()

            # Сохраняем отдельную запись клика
            BattleClick.objects.create(
                participant=participant,
                battle=battle,
                clicks=data.get('clicks', 1),
                coins=data.get('coins', 0),
                session_id=data.get('session_id', '')
            )

            # Обновляем кэш каждые 10 кликов
            if participant.clicks % 10 == 0:
                BattleOptimizer.update_battle_cache(self.battle_id)

        except Exception as e:
            print(f"Error saving click: {e}")

    async def click_update(self, event):
        await self.send(text_data=json.dumps({
            'action': 'click_update',
            'player_id': event['player_id'],
            'clicks': event['clicks'],
            'timestamp': event['timestamp']
        }))

    async def send_initial_data(self):
        # Получаем данные из кэша
        cache_key = f'battle_stats_{self.battle_id}'
        cached_stats = cache.get(cache_key)

        if cached_stats:
            stats = cached_stats
        else:
            # Получаем из базы данных
            stats = await database_sync_to_async(
                self.get_battle_stats_from_db
            )(self.battle_id)

        await self.send(text_data=json.dumps({
            'action': 'init',
            'battle_id': self.battle_id,
            'stats': stats,
            'your_player_id': self.player_id
        }))

    def get_battle_stats_from_db(self, battle_id):
        from .models import Battle, BattleParticipant
        from django.db.models import Count, Sum, Max

        battle = Battle.objects.filter(id=battle_id).first()
        if not battle:
            return {}

        participants = battle.participants.all()

        return {
            'id': battle.id,
            'name': battle.name,
            'status': battle.status,
            'total_clicks': participants.aggregate(total=Sum('clicks'))['total'] or 0,
            'total_participants': participants.count(),
            'top_score': participants.aggregate(top=Max('clicks'))['top'] or 0,
            'top_player': participants.order_by('-clicks').first().player_id if participants.exists() else None
        }