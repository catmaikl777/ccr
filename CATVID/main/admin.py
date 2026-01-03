# main/admin.py
from django.contrib import admin
from .models import Upgrade, Player, PlayerAutoClicker, Skin, PlayerSkin, Box, BoxDrop, BoxOpening
# admin.py - добавьте в начало
from .models import Achievement, PlayerAchievement

@admin.register(Upgrade)
class UpgradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'upgrade_type', 'level', 'current_cost', 'max_level')
    list_filter = ('upgrade_type',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'upgrade_type')
        }),
        ('Стоимость и уровни', {
            'fields': ('base_cost', 'current_cost', 'cost_multiplier', 'level', 'max_level')
        }),
        ('Эффекты', {
            'fields': ('click_power_increase', 'auto_clicker_speed', 'critical_chance', 'coin_multiplier'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PlayerAutoClicker)
class PlayerAutoClickerAdmin(admin.ModelAdmin):
    list_display = ('player', 'clicks_per_second', 'is_active', 'last_auto_click')
    list_filter = ('is_active',)
    search_fields = ('player__user__username',)

@admin.register(Skin)
class SkinAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_name', 'is_free', 'required_clicks', 'required_coins', 'order')
    list_filter = ('is_free',)
    list_editable = ('order', 'is_free', 'required_clicks', 'required_coins')
    search_fields = ('name', 'description')

@admin.register(PlayerSkin)
class PlayerSkinAdmin(admin.ModelAdmin):
    list_display = ('player', 'skin', 'unlocked_at', 'is_selected')
    list_filter = ('is_selected', 'unlocked_at')
    search_fields = ('player__user__username', 'skin__name')

# admin.py - добавить
@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'achievement_type', 'rarity', 'reward_coins', 'order')
    list_filter = ('achievement_type', 'rarity', 'is_secret')
    list_editable = ('order', 'rarity')
    search_fields = ('name', 'description')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'achievement_type', 'rarity', 'icon', 'order')
        }),
        ('Требования', {
            'fields': ('required_clicks', 'required_coins', 'required_upgrades',
                      'required_battles', 'required_wins', 'required_collection'),
            'classes': ('collapse',)
        }),
        ('Награда', {
            'fields': ('reward_coins', 'reward_click_power', 'reward_auto_clicker',
                      'reward_critical_chance', 'reward_coin_multiplier', 'unlock_skin', 'badge_color'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('is_secret', 'secret_description'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(admin.ModelAdmin):
    list_display = ('player', 'achievement', 'unlocked_at', 'is_new')
    list_filter = ('unlocked_at', 'is_new')
    search_fields = ('player__user__username', 'achievement__name')
    list_editable = ('is_new',)
    date_hierarchy = 'unlocked_at'


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active')
    list_filter = ('is_active',)
    list_editable = ('price', 'is_active')
    search_fields = ('name', 'description')


class BoxDropInline(admin.TabularInline):
    model = BoxDrop
    extra = 1
    fields = ('item_type', 'item_value', 'drop_chance', 'is_rare')


@admin.register(BoxDrop)
class BoxDropAdmin(admin.ModelAdmin):
    list_display = ('box', 'item_type', 'item_value', 'drop_chance', 'is_rare')
    list_filter = ('item_type', 'is_rare', 'box')
    search_fields = ('item_value',)
    list_editable = ('drop_chance', 'is_rare')


@admin.register(BoxOpening)
class BoxOpeningAdmin(admin.ModelAdmin):
    list_display = ('player', 'box', 'item_type', 'item_value', 'is_rare', 'opened_at')
    list_filter = ('item_type', 'is_rare', 'opened_at', 'box')
    search_fields = ('player__user__username', 'item_value')
    date_hierarchy = 'opened_at'
    readonly_fields = ('opened_at',)