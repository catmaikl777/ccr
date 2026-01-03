from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

class ResourceTrade(models.Model):
    """Модель для асинхронной торговли ресурсами"""
    RESOURCE_TYPES = [
        ('clicks', 'Клики'),
        ('coins', 'Монеты'),
        ('upgrades', 'Улучшения'),
        ('skins', 'Скины'),
    ]
    
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='offers_made')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    resource_amount = models.CharField(max_length=100)  # Для хранения имени скина или числа
    want_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    want_amount = models.CharField(max_length=100)  # Для хранения имени скина или числа
    status = models.CharField(max_length=20, default='active')  # active, completed, cancelled
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.player} предлагает {self.resource_amount} {self.resource_type} за {self.want_amount} {self.want_type}"
        
    def get_resource_amount_display(self):
        if self.resource_type == 'skins':
            return Skin.objects.get(image_name=self.resource_amount).name
        return self.resource_amount
        
    def get_want_amount_display(self):
        if self.want_type == 'skins':
            return Skin.objects.get(image_name=self.want_amount).name
        return self.want_amount


# models.py - обновить модель Player
# models.py - добавить в класс Player
class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    clicks = models.IntegerField(default=0)
    coins = models.IntegerField(default=0)
    click_power = models.IntegerField(default=1)
    auto_clicker_power = models.IntegerField(default=0)
    critical_chance = models.FloatField(default=0.0)
    coin_multiplier = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    current_skin = models.CharField(max_length=100, default='cat.png')  # Текущий скин

    def __str__(self):
        return f"Player: {self.user.username if self.user else 'Anonymous'} - {self.coins} coins"

    def get_available_skins(self):
        """Получить список доступных скинов для игрока"""
        # Получаем все скины, которые игрок может использовать
        available_skins = []
        
        # Получаем все скины из базы данных
        all_skins = Skin.objects.all()
        
        for skin in all_skins:
            if skin.is_unlocked_for_player(self):
                available_skins.append(skin)
                
        return available_skins
        
    def has_skin(self, skin_name):
        """Проверить, есть ли у игрока определенный скин"""
        try:
            skin = Skin.objects.get(image_name=skin_name)
            return self.unlocked_skins.filter(skin=skin).exists()
        except Skin.DoesNotExist:
            return False
            
    def can_unlock_skin(self, skin):
        """Проверить, может ли игрок разблокировать скин"""
        return skin.is_unlocked_for_player(self)
        
    def unlock_skin(self, skin):
        """Разблокировать скин для игрока"""
        if not self.can_unlock_skin(skin):
            return False
            
        # Проверяем, не разблокирован ли уже скин
        player_skin, created = PlayerSkin.objects.get_or_create(
            player=self,
            skin=skin
        )
        
        # Если скин не бесплатный, списываем монеты
        if not skin.is_free and skin.required_coins > 0:
            if self.coins >= skin.required_coins:
                self.coins -= skin.required_coins
                self.save()
            else:
                return False
                
        return True

    def unlock_skin_from_box(self, skin_name):
        """Разблокировать скин из ящика"""
        try:
            skin = Skin.objects.get(image_name=skin_name)
            player_skin, created = PlayerSkin.objects.get_or_create(
                player=self,
                skin=skin
            )
            return created
        except Skin.DoesNotExist:
            return False


class Battle(models.Model):
    """Модель баттла между двумя игроками"""
    STATUS_CHOICES = [
        ('waiting', 'Ожидание соперника'),
        ('active', 'В процессе'),
        ('finished', 'Завершен'),
    ]

    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battles_as_player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battles_as_player2', null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    duration = models.IntegerField(default=60)  # длительность баттла в секундах
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='won_battles')


class BattleParticipant(models.Model):
    """Данные участника в конкретном баттле"""
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clicks = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    is_ready = models.BooleanField(default=False)


class BattleInvite(models.Model):
    """Приглашения в баттлы"""
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invites')
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Ожидает'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

# models.py - добавить после Player
class Skin(models.Model):
    name = models.CharField(max_length=100)
    image_name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    is_free = models.BooleanField(default=False)  # Теперь не все скины бесплатные
    price = models.IntegerField(default=0)  # Цена скина в монетах
    unlock_requirement = models.CharField(max_length=200, blank=True, null=True)
    required_clicks = models.IntegerField(default=0)
    required_coins = models.IntegerField(default=0)
    rarity = models.CharField(max_length=20, default='common')  # Редкость скина
    order = models.IntegerField(default=0)  # Порядок отображения

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        price_info = f" - {self.price} монет" if not self.is_free else " - Бесплатно"
        return f"{self.name}{price_info}"

    def is_unlocked_for_player(self, player):
        """Проверить, разблокирован ли скин для игрока"""
        # Проверяем, не разблокирован ли уже скин
        if PlayerSkin.objects.filter(player=player, skin=self).exists():
            return True

        # Проверяем требования по кликам
        if self.required_clicks > 0 and player.clicks < self.required_clicks:
            return False

        # Проверяем, достаточно ли монет для покупки
        if self.price > 0 and player.coins < self.price:
            return False

        return True


class PlayerSkin(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='unlocked_skins')
    skin = models.ForeignKey(Skin, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    is_selected = models.BooleanField(default=False)

    class Meta:
        unique_together = ['player', 'skin']

    def __str__(self):
        return f"{self.player} - {self.skin.name}"


class Upgrade(models.Model):
    UPGRADE_TYPES = [
        ('click_power', 'Усиление клика'),
        ('auto_clicker', 'Автокликер'),
        ('critical_chance', 'Шанс крита'),
        ('coin_multiplier', 'Множитель монет'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    upgrade_type = models.CharField(max_length=20, choices=UPGRADE_TYPES, default='click_power')

    # Поля стоимости и уровней
    base_cost = models.IntegerField(default=10)
    current_cost = models.IntegerField(default=10)
    level = models.IntegerField(default=1)
    cost_multiplier = models.FloatField(default=1.5)
    max_level = models.IntegerField(default=20)

    # Эффекты в зависимости от типа
    click_power_increase = models.IntegerField(default=0)  # Для усиления клика
    auto_clicker_speed = models.IntegerField(default=0)  # Скорость автокликера (кликов в секунду)
    critical_chance = models.FloatField(default=0)  # Шанс крита (%)
    coin_multiplier = models.FloatField(default=1.0)  # Множитель монет

    def __str__(self):
        return f"{self.name} (Уровень {self.level})"

    def calculate_next_cost(self):
        """Рассчитать стоимость следующего уровня"""
        return int(self.base_cost * (self.cost_multiplier ** self.level))

    def get_effect_value(self):
        """Получить значение эффекта в зависимости от типа"""
        if self.upgrade_type == 'click_power':
            return self.click_power_increase
        elif self.upgrade_type == 'auto_clicker':
            return self.auto_clicker_speed
        elif self.upgrade_type == 'critical_chance':
            return self.critical_chance
        elif self.upgrade_type == 'coin_multiplier':
            return self.coin_multiplier
        return 0


class PlayerUpgrade(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_upgrades')
    upgrade = models.ForeignKey(Upgrade, on_delete=models.CASCADE, related_name='player_upgrades')
    level = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['player', 'upgrade']

    def __str__(self):
        return f"{self.player} - {self.upgrade} (Уровень {self.level})"


# models.py - добавить после модели Upgrade
class PlayerAutoClicker(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name='auto_clicker')
    clicks_per_second = models.IntegerField(default=0)
    last_auto_click = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Автокликер игрока {self.player}"


# models.py - добавить после других моделей
class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('clicks', 'Клики'),
        ('coins', 'Монеты'),
        ('upgrades', 'Улучшения'),

        ('special', 'Специальные'),
        ('collection', 'Коллекция'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = models.CharField(max_length=100, default='fas fa-trophy')

    # Требования для получения
    required_clicks = models.BigIntegerField(default=0)
    required_coins = models.BigIntegerField(default=0)
    required_upgrades = models.IntegerField(default=0)

    required_wins = models.IntegerField(default=0)
    required_collection = models.JSONField(default=dict, blank=True, null=True)  # Для специальных требований

    # Награда
    reward_coins = models.BigIntegerField(default=0)
    reward_click_power = models.IntegerField(default=0)
    reward_auto_clicker = models.IntegerField(default=0)
    reward_critical_chance = models.FloatField(default=0)
    reward_coin_multiplier = models.FloatField(default=0)
    unlock_skin = models.CharField(max_length=100, blank=True, null=True)  # Разблокируемый скин
    badge_color = models.CharField(max_length=20, default='#FFD700')  # Цвет бейджа

    # Редкость
    RARITY_CHOICES = [
        ('common', 'Обычное'),
        ('uncommon', 'Необычное'),
        ('rare', 'Редкое'),
        ('epic', 'Эпическое'),
        ('legendary', 'Легендарное'),
    ]
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')

    # Порядок и видимость
    order = models.IntegerField(default=0)
    is_secret = models.BooleanField(default=False)  # Скрытое достижение
    secret_description = models.TextField(blank=True, null=True)  # Описание до разблокировки

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'rarity', 'name']
        indexes = [
            models.Index(fields=['achievement_type']),
            models.Index(fields=['rarity']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"

    def get_progress(self, player):
        """Получить прогресс игрока для этого достижения"""
        progress = {
            'current': 0,
            'required': 0,
            'percentage': 0,
            'completed': False
        }

        if self.achievement_type == 'clicks':
            progress['current'] = player.clicks
            progress['required'] = self.required_clicks
        elif self.achievement_type == 'coins':
            progress['current'] = player.coins
            progress['required'] = self.required_coins
        elif self.achievement_type == 'upgrades':
            from .models import Upgrade
            progress['current'] = Upgrade.objects.filter(level__gt=1).count()
            progress['required'] = self.required_upgrades

        elif self.achievement_type == 'special':
            # Специальные достижения обрабатываются отдельно
            progress['current'] = 0
            progress['required'] = 1

        if progress['required'] > 0:
            progress['percentage'] = min(100, (progress['current'] / progress['required']) * 100)
            progress['completed'] = progress['current'] >= progress['required']

        return progress

    def get_icon_class(self):
        """Получить класс иконки с цветом в зависимости от редкости"""
        rarity_colors = {
            'common': '#808080',
            'uncommon': '#1EFF00',
            'rare': '#0070DD',
            'epic': '#A335EE',
            'legendary': '#FF8000',
        }
        return {
            'icon': self.icon,
            'color': rarity_colors.get(self.rarity, '#FFD700')
        }


class PlayerAchievement(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    progress_data = models.JSONField(default=dict)  # Для хранения прогресса на момент разблокировки
    is_new = models.BooleanField(default=True)  # Помечать новые достижения

    class Meta:
        unique_together = ['player', 'achievement']
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"{self.player} - {self.achievement.name}"

    def apply_reward(self, player):
        """Применить награду достижения к игроку"""
        if self.achievement.reward_coins > 0:
            player.coins += self.achievement.reward_coins

        if self.achievement.reward_click_power > 0:
            player.click_power += self.achievement.reward_click_power

        if self.achievement.reward_auto_clicker > 0:
            player.auto_clicker_power += self.achievement.reward_auto_clicker

        if self.achievement.reward_critical_chance > 0:
            player.critical_chance += self.achievement.reward_critical_chance

        if self.achievement.reward_coin_multiplier > 0:
            player.coin_multiplier += self.achievement.reward_coin_multiplier

        if self.achievement.unlock_skin:
            # Разблокируем скин для игрока
            player.current_skin = self.achievement.unlock_skin
            # Можно добавить в коллекцию скинов

        player.save()


# Модели для системы ящиков
class Box(models.Model):
    """Модель ящика для получения скинов"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()  # Цена в монетах
    image = models.CharField(max_length=100, default='box.svg')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - {self.price} монет"


class BoxDrop(models.Model):
    """Возможные выпадения из ящика"""
    ITEM_TYPES = [
        ('skin', 'Скин'),
        ('coins', 'Монеты'),
        ('clicks', 'Клики'),
    ]
    
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='drops')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES)
    item_value = models.CharField(max_length=100)  # Название скина или количество
    drop_chance = models.FloatField()  # Шанс выпадения (0.0-1.0)
    is_rare = models.BooleanField(default=False)  # Редкий предмет
    
    class Meta:
        ordering = ['-is_rare', '-drop_chance']
    
    def __str__(self):
        return f"{self.box.name} - {self.item_value} ({self.drop_chance*100}%)"


class BoxOpening(models.Model):
    """История открытия ящиков"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='box_openings')
    box = models.ForeignKey(Box, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=10)
    item_value = models.CharField(max_length=100)
    is_rare = models.BooleanField(default=False)
    opened_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-opened_at']
    
    def __str__(self):
        return f"{self.player} получил {self.item_value} из {self.box.name}"