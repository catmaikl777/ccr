# main/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Получить элемент из словаря по ключу"""
    return dictionary.get(key)

@register.filter
def get_rarity_color(rarity):
    """Получить цвет для редкости"""
    colors = {
        'common': '#808080',
        'uncommon': '#1EFF00',
        'rare': '#0070DD',
        'epic': '#A335EE',
        'legendary': '#FF8000',
    }
    return colors.get(rarity, '#FFD700')