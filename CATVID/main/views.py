from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie, csrf_exempt
from .models import Player, Upgrade, PlayerUpgrade, PlayerAutoClicker, Skin, PlayerSkin, Battle, BattleParticipant, BattleInvite, Box, BoxDrop, BoxOpening
import json
import os
from django.conf import settings
from django.core.cache import cache
from . import models
from django.conf.urls.static import static
from django.utils import timezone
from django.shortcuts import get_object_or_404
import random

# views.py - оптимизированные представления
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import ListView
import time
from .models import Achievement, PlayerAchievement
from .achievements_checker import AchievementChecker


@login_required
def achievements_view(request):
    """Страница достижений"""
    player = Player.objects.get(user=request.user)
    checker = AchievementChecker(player)

    # Получаем все достижения сгруппированные по типам
    all_achievements = {}
    for achievement_type, name in Achievement.ACHIEVEMENT_TYPES:
        achievements = Achievement.objects.filter(achievement_type=achievement_type).order_by('order', 'rarity')

        achievements_with_progress = []
        for achievement in achievements:
            player_has = PlayerAchievement.objects.filter(
                player=player,
                achievement=achievement
            ).first()

            progress = achievement.get_progress(player)

            achievements_with_progress.append({
                'achievement': achievement,
                'unlocked': player_has is not None,
                'player_achievement': player_has,
                'progress': progress,
                'is_secret': achievement.is_secret and not player_has,
                'secret_description': achievement.secret_description if achievement.is_secret and not player_has else None
            })

        all_achievements[achievement_type] = {
            'name': name,
            'achievements': achievements_with_progress
        }

    # Статистика
    stats = checker.get_achievement_stats()

    # Проверяем новые достижения
    new_achievements = PlayerAchievement.objects.filter(
        player=player,
        is_new=True
    ).select_related('achievement').order_by('-unlocked_at')[:10]

    context = {
        'player': player,
        'all_achievements': all_achievements,
        'stats': stats,
        'new_achievements': new_achievements,
        'achievement_types': Achievement.ACHIEVEMENT_TYPES,
        'rarity_colors': {
            'common': '#808080',
            'uncommon': '#1EFF00',
            'rare': '#0070DD',
            'epic': '#A335EE',
            'legendary': '#FF8000',
        }
    }

    return render(request, 'main/achievements.html', context)


@login_required
@csrf_protect
def check_achievements(request):
    """API для проверки достижений"""
    if request.method == 'POST':
        try:
            player = Player.objects.get(user=request.user)
            checker = AchievementChecker(player)

            unlocked_achievements = checker.check_all_achievements()

            # Получаем новые достижения
            new_achievements = PlayerAchievement.objects.filter(
                player=player,
                is_new=True
            ).select_related('achievement')

            return JsonResponse({
                'success': True,
                'unlocked_count': len(unlocked_achievements),
                'new_achievements': [
                    {
                        'id': ach.id,
                        'name': ach.achievement.name,
                        'description': ach.achievement.description,
                        'rarity': ach.achievement.rarity,
                        'icon': ach.achievement.icon,
                        'reward_coins': ach.achievement.reward_coins,
                        'unlocked_at': ach.unlocked_at.isoformat(),
                    }
                    for ach in new_achievements
                ],
                'stats': checker.get_achievement_stats()
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid method'})



@login_required
@csrf_protect
def mark_achievement_seen(request, achievement_id):
    """Отметить достижение как просмотренное"""
    if request.method == 'POST':
        try:
            player = Player.objects.get(user=request.user)
            player_achievement = PlayerAchievement.objects.get(
                player=player,
                id=achievement_id
            )

            player_achievement.is_new = False
            player_achievement.save()

            return JsonResponse({'success': True})
        except PlayerAchievement.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Achievement not found'})

    return JsonResponse({'success': False, 'error': 'Invalid method'})



@login_required
def get_achievement_progress(request):
    """Получить прогресс по достижениям"""
    player = Player.objects.get(user=request.user)
    checker = AchievementChecker(player)

    return JsonResponse({
        'success': True,
        'stats': checker.get_achievement_stats(),
        'next_achievements': [
            {
                'name': item['achievement'].name,
                'progress': item['progress'],
                'icon': item['achievement'].icon,
                'rarity': item['achievement'].rarity,
            }
            for item in checker.get_next_achievements()
        ]
    })


# views.py
@login_required
def find_opponent(request):
    """Поиск случайного соперника"""
    # Ищем открытые баттлы
    open_battles = Battle.objects.filter(
        status='waiting'
    ).exclude(player1=request.user)

    if open_battles.exists():
        battle = open_battles.first()
        battle.player2 = request.user
        battle.status = 'active'
        battle.started_at = timezone.now()
        battle.save()

        BattleParticipant.objects.create(
            battle=battle,
            user=request.user,
            clicks=0,
            score=0
        )
        return JsonResponse({
            'found': True,
            'battle_id': battle.id,
            'opponent': battle.player1.username
        })

    return JsonResponse({'found': False})


# views.py
@csrf_exempt
@login_required
def register_click(request, battle_id):
    """Регистрация клика игрока"""
    try:
        battle = Battle.objects.get(id=battle_id, status='active')
        participant = BattleParticipant.objects.get(
            battle=battle,
            user=request.user
        )

        participant.clicks += 1
        participant.score += 1  # Можно добавить множители
        participant.save()

        return JsonResponse({
            'success': True,
            'clicks': participant.clicks,
            'score': participant.score
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# views.py
import time
from django.http import JsonResponse


# views.py - обновите функцию get_battle_updates

@login_required
def get_battle_updates(request, battle_id):
    """Long Polling для получения обновлений баттла"""
    try:
        # Используем оптимизированный запрос
        battle = Battle.objects.select_related(
            'player1', 'player2', 'winner'
        ).prefetch_related(
            'participants__user'
        ).get(id=battle_id)

        # Время ожидания (таймаут)
        timeout = 30
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Получаем состояние баттла из кэша или рассчитываем
            state = get_battle_state(battle_id)

            if not state:
                return JsonResponse({'error': 'Battle not found'})

            # Проверяем, изменились ли данные
            last_check = request.GET.get('last_check', '')
            current_hash = hash(str(state))

            if current_hash != last_check:
                return JsonResponse({
                    'data': state,
                    'hash': current_hash,
                    'has_update': True
                })

            time.sleep(0.5)  # Пауза между проверками

        return JsonResponse({'has_update': False, 'timeout': True})

    except Battle.DoesNotExist:
        return JsonResponse({'error': 'Battle not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


# views.py - добавьте эту функцию после импортов

def calculate_battle_state(battle_id):
    """Рассчитать состояние баттла для кэширования"""
    try:
        # Используем оптимизированный запрос
        battle = Battle.objects.select_related(
            'player1', 'player2', 'winner'
        ).prefetch_related(
            'participants__user'
        ).get(id=battle_id)

        participants_data = []
        total_clicks = 0

        for participant in battle.participants.all():
            participants_data.append({
                'user_id': participant.user.id,
                'username': participant.user.username,
                'clicks': participant.clicks,
                'score': participant.score,
                'is_ready': participant.is_ready,
            })
            total_clicks += participant.clicks

        state = {
            'battle_id': battle.id,
            'status': battle.status,
            'player1': {
                'id': battle.player1.id,
                'username': battle.player1.username,
            } if battle.player1 else None,
            'player2': {
                'id': battle.player2.id if battle.player2 else None,
                'username': battle.player2.username if battle.player2 else None,
            },
            'winner': {
                'id': battle.winner.id if battle.winner else None,
                'username': battle.winner.username if battle.winner else None,
            } if battle.winner else None,
            'participants': participants_data,
            'total_clicks': total_clicks,
            'created_at': battle.created_at.isoformat() if battle.created_at else None,
            'started_at': battle.started_at.isoformat() if battle.started_at else None,
            'finished_at': battle.finished_at.isoformat() if battle.finished_at else None,
            'duration': battle.duration,
            'time_left': None,
        }

        # Рассчитываем оставшееся время
        if battle.status == 'active' and battle.started_at:
            elapsed = (timezone.now() - battle.started_at).total_seconds()
            state['time_left'] = max(0, battle.duration - int(elapsed))

        return state
    except Battle.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error calculating battle state: {e}")
        return None

# Кэширование результатов
from django.core.cache import cache

def get_battle_state(battle_id):
    cache_key = f'battle_state_{battle_id}'
    state = cache.get(cache_key)
    if not state:
        state = calculate_battle_state(battle_id)
        cache.set(cache_key, state, timeout=5)  # Кэш на 5 секунд
    return state

# Главная страница - для всех пользователей
@ensure_csrf_cookie
def index(request):
    try:
        # Если пользователь авторизован, используем его профиль
        if request.user.is_authenticated:
            try:
                player = Player.objects.get(user=request.user)
            except Player.DoesNotExist:
                # Если у пользователя нет профиля, создаем его
                player = Player.objects.create(user=request.user)
                request.session['player_id'] = player.id
        else:
            # Для анонимных пользователей используем сессию
            player_id = request.session.get('player_id')
            player = None

            if player_id:
                try:
                    player = Player.objects.get(id=player_id)
                except Player.DoesNotExist:
                    player = None

            if not player:
                player = Player.objects.create()
                request.session['player_id'] = player.id

        # Убедимся, что player определен
        if not player:
            raise ValueError("Не удалось создать или получить игрока")

        upgrades = list(Upgrade.objects.all())

        # Персональные уровни/цены апгрейдов для игрока
        player_upgrades = {
            pu.upgrade_id: pu
            for pu in PlayerUpgrade.objects.filter(player=player)
        }

        for upgrade in upgrades:
            pu = player_upgrades.get(upgrade.id)
            player_level = pu.level if pu else 0

            upgrade.player_level = player_level
            upgrade.player_cost = int(upgrade.base_cost * (upgrade.cost_multiplier ** player_level))
            upgrade.player_next_cost = int(upgrade.base_cost * (upgrade.cost_multiplier ** (player_level + 1)))
            upgrade.player_is_max_level = player_level >= upgrade.max_level

        # Получаем текущий скин игрока
        if not player.current_skin:
            player.current_skin = 'cat.png'
            player.save()

        # Получаем доступные ящики
        boxes = Box.objects.filter(is_active=True)

        context = {
            'player': player,
            'upgrades': upgrades,
            'current_skin': player.current_skin,
            'boxes': boxes,
        }

        return render(request, 'main/index.html', context)

    except Exception as e:
        # Логируем ошибку для отладки
        print(f"Error in index view: {e}")
        # Показываем пользователю страницу с ошибкой
        messages.error(request, 'Произошла ошибка при загрузке игры. Попробуйте обновить страницу.')
        return render(request, 'main/error.html', {'error': str(e)})


# Регистрация
@csrf_protect
def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Проверка паролей
        if password1 != password2:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'main/register.html')

        # Проверка существования пользователя
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return render(request, 'main/register.html')

        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует.')
            return render(request, 'main/register.html')

        # Создание пользователя
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )

            # Создаем профиль игрока
            player = Player.objects.create(user=user)

            # Автоматически логиним пользователя
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}! Регистрация прошла успешно.')
            return redirect('index')

        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            return render(request, 'main/register.html')

    # Для GET запроса показываем форму
    return render(request, 'main/register.html')



# Авторизация
@csrf_protect
# Авторизация
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')

            # Перенаправляем на следующую страницу или на главную
            next_url = request.POST.get('next')
            if next_url and next_url.strip():  # Проверяем, что next_url не пустой
                return redirect(next_url)
            else:
                return redirect('index')  # По умолчанию на главную
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
            # Сохраняем next параметр для повторной попытки
            next_param = request.POST.get('next', '')
            return render(request, 'main/login.html', {'next': next_param})

    # Для GET запроса показываем форму
    # Получаем next из GET параметров
    next_param = request.GET.get('next', '')
    return render(request, 'main/login.html', {'next': next_param})


# Выход
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    next_url = request.GET.get('next', 'login')  # По умолчанию на страницу входа
    return redirect(next_url)


# Обработчик кликов
@csrf_protect
def click(request):
    if request.method == 'POST':
        try:
            # Логируем запрос для отладки
            print(f"Click request received. Content-Type: {request.content_type}")
            print(f"Request body: {request.body}")

            data = json.loads(request.body)
            player_id = data.get('player_id')
            clicks = data.get('clicks', 1)

            print(f"Player ID from request: {player_id}")

            if not player_id:
                print("No player_id in request data")
                return JsonResponse({'error': 'Player ID is required'}, status=400)

            try:
                clicks = int(clicks)
            except (TypeError, ValueError):
                clicks = 1

            if clicks < 1:
                clicks = 1

            # Попробуем получить игрока
            try:
                player = Player.objects.get(id=player_id)
                print(f"Player found: {player.id}, coins: {player.coins}, clicks: {player.clicks}, click_power: {player.click_power}")

                # Увеличиваем счетчики
                player.clicks += clicks
                coins_earned = player.click_power * clicks
                player.coins += coins_earned
                player.save()

                print(f"Player updated: coins: {player.coins}, clicks: {player.clicks}")

                # Проверяем достижения
                from .achievements_checker import AchievementChecker
                checker = AchievementChecker(player)
                unlocked = checker.check_all_achievements()
                if unlocked:
                    print(f"Unlocked {len(unlocked)} achievements: {[ach.name for ach in unlocked]}")

                return JsonResponse({
                    'coins': player.coins,
                    'clicks': player.clicks,
                    'click_power': player.click_power,
                    'coins_earned': coins_earned,
                    'success': True
                })

            except Player.DoesNotExist:
                print(f"Player with ID {player_id} not found")
                return JsonResponse({'error': 'Player not found'}, status=404)

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Unexpected error in click view: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# views.py - обновить функцию buy_upgrade
@csrf_protect
def buy_upgrade(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player_id = data.get('player_id')
            upgrade_id = data.get('upgrade_id')

            if not player_id or not upgrade_id:
                return JsonResponse({'error': 'Не указаны необходимые параметры'}, status=400)

            player = Player.objects.get(id=player_id)
            upgrade = Upgrade.objects.get(id=upgrade_id)

            player_upgrade, _ = PlayerUpgrade.objects.get_or_create(
                player=player,
                upgrade=upgrade,
                defaults={'level': 0}
            )

            # Проверяем максимальный уровень (персонально для игрока)
            if player_upgrade.level >= upgrade.max_level:
                return JsonResponse({
                    'success': False,
                    'error': 'Достигнут максимальный уровень улучшения'
                })

            # Получаем текущую стоимость (персонально для игрока)
            current_cost = int(upgrade.base_cost * (upgrade.cost_multiplier ** player_upgrade.level))

            if player.coins >= current_cost:
                player.coins -= current_cost

                # Применяем эффект в зависимости от типа улучшения
                upgrade_type = upgrade.upgrade_type

                if upgrade_type == 'click_power':
                    player.click_power += upgrade.click_power_increase
                elif upgrade_type == 'auto_clicker':
                    player.auto_clicker_power += upgrade.auto_clicker_speed
                    # Создаем или обновляем автокликер игрока
                    auto_clicker, created = PlayerAutoClicker.objects.get_or_create(
                        player=player,
                        defaults={
                            'clicks_per_second': player.auto_clicker_power,
                            'is_active': True
                        }
                    )
                    if not created:
                        auto_clicker.clicks_per_second = player.auto_clicker_power
                        auto_clicker.is_active = True
                        auto_clicker.save()
                elif upgrade_type == 'critical_chance':
                    player.critical_chance += upgrade.critical_chance
                elif upgrade_type == 'coin_multiplier':
                    player.coin_multiplier += upgrade.coin_multiplier

                # Увеличиваем уровень улучшения (персонально)
                player_upgrade.level += 1

                # Рассчитываем стоимость следующего уровня (персонально)
                next_cost = int(upgrade.base_cost * (upgrade.cost_multiplier ** player_upgrade.level))

                player.save()
                player_upgrade.save()

                return JsonResponse({
                    'success': True,
                    'coins': player.coins,
                    'click_power': player.click_power,
                    'auto_clicker_power': player.auto_clicker_power,
                    'critical_chance': player.critical_chance,
                    'coin_multiplier': player.coin_multiplier,
                    'upgrade_cost': next_cost,
                    'upgrade_level': player_upgrade.level,
                    'next_cost': int(upgrade.base_cost * (upgrade.cost_multiplier ** (player_upgrade.level + 1))),
                    'is_max_level': player_upgrade.level >= upgrade.max_level,
                    'max_level': upgrade.max_level,
                    'upgrade_type': upgrade_type
                })

                # После покупки улучшения
                checker = AchievementChecker(player)
                checker.check_all_achievements()
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Недостаточно монет. Нужно: {current_cost}',
                    'required_coins': current_cost,
                    'player_coins': player.coins
                })

        except (Player.DoesNotExist, Upgrade.DoesNotExist):
            return JsonResponse({'error': 'Not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Ошибка при покупке улучшения: {e}")
            return JsonResponse({'error': f'Внутренняя ошибка сервера: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Неверный метод запроса'}, status=405)


# Добавим функцию для авто-кликов
@csrf_protect
@csrf_exempt
def auto_click(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player_id = data.get('player_id')

            if not player_id:
                return JsonResponse({'error': 'Player ID is required'}, status=400)

            player = Player.objects.get(id=player_id)

            # Проверяем, есть ли у игрока автокликер
            try:
                auto_clicker = PlayerAutoClicker.objects.get(player=player)
                clicks_per_second = auto_clicker.clicks_per_second

                if clicks_per_second > 0 and auto_clicker.is_active:
                    # Рассчитываем время с последнего обновления
                    from django.utils import timezone
                    now = timezone.now()
                    time_diff = (now - auto_clicker.last_auto_click).total_seconds()

                    # Максимальный интервал - 10 секунд
                    max_interval = 10
                    if time_diff > max_interval:
                        time_diff = max_interval

                    # Рассчитываем количество кликов за прошедшее время
                    clicks_earned = int(clicks_per_second * time_diff)

                    if clicks_earned > 0:
                        # Начисляем монеты за автоклики
                        coins_earned = clicks_earned * player.click_power
                        player.coins += coins_earned
                        player.clicks += clicks_earned
                        player.save()

                        # Обновляем время последнего автоклика
                        auto_clicker.last_auto_click = now
                        auto_clicker.save()

                        return JsonResponse({
                            'success': True,
                            'coins': player.coins,
                            'clicks': player.clicks,
                            'coins_earned': coins_earned,
                            'auto_clicks': clicks_earned,
                            'time_diff': time_diff
                        })
                    else:
                        return JsonResponse({
                            'success': True,
                            'coins': player.coins,
                            'clicks': player.clicks,
                            'coins_earned': 0,
                            'auto_clicks': 0
                        })

            except PlayerAutoClicker.DoesNotExist:
                return JsonResponse({
                    'success': True,
                    'coins': player.coins,
                    'clicks': player.clicks,
                    'coins_earned': 0,
                    'auto_clicks': 0
                })

        except Player.DoesNotExist:
            return JsonResponse({'error': 'Игрок не найден'}, status=404)
        except Exception as e:
            print(f"Ошибка в auto_click: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Неверный метод'}, status=405)


# views.py - добавить новую функцию
@csrf_protect
def get_auto_clicker_info(request, player_id):
    """Получить информацию об автокликере игрока"""
    try:
        player = Player.objects.get(id=player_id)

        try:
            auto_clicker = PlayerAutoClicker.objects.get(player=player)
            return JsonResponse({
                'has_auto_clicker': True,
                'clicks_per_second': auto_clicker.clicks_per_second,
                'is_active': auto_clicker.is_active,
                'last_auto_click': auto_clicker.last_auto_click.isoformat()
            })
        except PlayerAutoClicker.DoesNotExist:
            return JsonResponse({
                'has_auto_clicker': False,
                'clicks_per_second': 0
            })

    except Player.DoesNotExist:
        return JsonResponse({'error': 'Игрок не найден'}, status=404)

# Таблица лидеров
def leaderboard_view(request):
    # Берем только игроков с привязанными пользователями
    players = Player.objects.filter(user__isnull=False).select_related('user').order_by('-coins')[:20]

    # Текущий игрок
    current_player = None
    current_rank = None

    if request.user.is_authenticated:
        try:
            current_player = Player.objects.get(user=request.user)
            # Определяем место текущего игрока
            all_players = list(Player.objects.filter(user__isnull=False).order_by('-coins'))
            for index, player in enumerate(all_players, 1):
                if player.id == current_player.id:
                    current_rank = index
                    break
        except Player.DoesNotExist:
            pass

    context = {
        'players': players,
        'current_player': current_player,
        'current_rank': current_rank,
    }
    return render(request, 'main/leaderbords.html', context)


# Простая страница для отладки ошибок
def error_view(request, error_message=""):
    return render(request, 'main/error.html', {'error': error_message})


# Тестовая страница для диагностики кликов
def test_click(request):
    return render(request, 'main/test_click.html')

# Тестовая страница для диагностики звуков
def sound_test_view(request):
    return render(request, 'main/sound-test.html')

def get_skins_list():
    """Получить список всех доступных скинов"""
    # Базовые скины
    default_skins = [
        'cat.png',
        'skin3.png',
        'skin4.png',
        'skin5.png',
        'skin6.png',
        'skin7.png',
        'skin8.png',
    ]

    # Начинаем с базовых скинов
    skins_found = []

    # Проверяем только существующие пути
    possible_paths = []

    # 1. Путь в приложении
    app_path = os.path.join(settings.BASE_DIR, 'main', 'static', 'main', 'skins')
    if os.path.exists(app_path):
        possible_paths.append(app_path)

    # 2. Путь в корне проекта
    project_path = os.path.join(settings.BASE_DIR, 'static', 'main', 'skins')
    if os.path.exists(project_path):
        possible_paths.append(project_path)

    # 3. Относительный путь
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    relative_path = os.path.join(current_dir, 'static', 'main', 'skins')
    if os.path.exists(relative_path):
        possible_paths.append(relative_path)

    # Ищем файлы скинов
    for skins_path in possible_paths:
        if skins_path:  # Проверяем, что путь не None
            try:
                for file in os.listdir(skins_path):
                    if file.lower().endswith('.png'):
                        skins_found.append(file)
                if skins_found:  # Если нашли скины, выходим
                    break
            except (FileNotFoundError, PermissionError, OSError) as e:
                print(f"Ошибка при доступе к {skins_path}: {e}")
                continue

    # Если нашли реальные файлы, используем их, иначе используем список по умолчанию
    final_skins = skins_found if skins_found else default_skins

    # Удаляем дубликаты и сортируем
    final_skins = list(dict.fromkeys(final_skins))
    final_skins.sort()

    return final_skins


# Страница выбора скина
@login_required
def skins_view(request):
    player = Player.objects.get(user=request.user)

    # Получаем все скины из базы данных
    all_skins = Skin.objects.all().order_by('order')

    # Проверяем, какие скины разблокированы для игрока
    for skin in all_skins:
        # Проверяем, разблокирован ли скин
        skin.is_unlocked = PlayerSkin.objects.filter(player=player, skin=skin).exists() or skin.is_free
        # Проверяем, может ли игрок разблокировать скин
        skin.can_unlock = (player.clicks >= skin.required_clicks and 
                          player.coins >= skin.price and 
                          not skin.is_unlocked)

    # Получаем текущий скин игрока
    current_skin = player.current_skin

    context = {
        'player': player,
        'skins': all_skins,
        'current_skin': current_skin,
    }
    return render(request, 'main/skins.html', context)


# Смена скина
@csrf_protect
@login_required
def change_skin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            skin_name = data.get('skin_name')

            player = Player.objects.get(user=request.user)

            # Получаем скин из базы данных
            try:
                skin = Skin.objects.get(image_name=skin_name)
            except Skin.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Скин не найден'
                })

            # Проверяем, есть ли у игрока этот скин
            has_skin = PlayerSkin.objects.filter(player=player, skin=skin).exists() or skin.is_free
            if has_skin:
                player.current_skin = skin_name
                player.save()

                return JsonResponse({
                    'success': True,
                    'message': f'Скин изменен на {skin.name}',
                    'current_skin': skin_name,
                    'skin_name': skin.name
                })
            else:
                # Проверяем, может ли игрок разблокировать скин
                can_unlock = (player.clicks >= skin.required_clicks and 
                             player.coins >= skin.price)
                if can_unlock:
                    # Разблокируем скин
                    if skin.price > 0:
                        player.coins -= skin.price
                        player.save()
                    
                    PlayerSkin.objects.get_or_create(
                        player=player,
                        skin=skin,
                        defaults={'unlocked_at': timezone.now()}
                    )
                    
                    player.current_skin = skin_name
                    player.save()

                    return JsonResponse({
                        'success': True,
                        'message': f'Скин {skin.name} разблокирован и установлен',
                        'current_skin': skin_name,
                        'skin_name': skin.name,
                        'unlocked': True
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': f'Вы не можете использовать этот скин. Требуется {skin.required_clicks} кликов и {skin.price} монет'
                    })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({
        'success': False,
        'error': 'Неверный метод запроса'
    })

# views.py
@login_required
def create_battle(request):
    """Создание нового баттла"""
    battle = Battle.objects.create(
        player1=request.user,
        status='waiting'
    )
    BattleParticipant.objects.create(
        battle=battle,
        user=request.user,
        clicks=0,
        score=0
    )
    return JsonResponse({'battle_id': battle.id, 'status': 'waiting'})

# API для получения текущего скина
# views.py
def get_current_skin(request, player_id):
    try:
        player = Player.objects.get(id=player_id)

        # Проверяем, существует ли файл скина
        import os
        from django.conf import settings

        skin_name = player.current_skin or 'cat.png'
        possible_paths = [
            os.path.join(settings.BASE_DIR, 'main', 'static', 'main', 'skins', skin_name),
            os.path.join(settings.BASE_DIR, 'static', 'main', 'skins', skin_name),
        ]

        skin_exists = False
        for skin_path in possible_paths:
            if os.path.exists(skin_path):
                skin_exists = True
                break

        # Если скин не существует, используем скин по умолчанию
        if not skin_exists:
            skin_name = 'cat.png'
            player.current_skin = skin_name
            player.save()

        return JsonResponse({
            'current_skin': skin_name,
            'skin_exists': skin_exists
        })
    except Player.DoesNotExist:
        return JsonResponse({
            'error': 'Игрок не найден'
        }, status=404)


# Добавим в index функцию обновления скина
# views.py - обновите функцию update_skin
@csrf_protect
def update_skin(request):
    """Обновить скин игрока (для AJAX запросов)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player_id = data.get('player_id')
            skin_name = data.get('skin_name')

            print(f"DEBUG: update_skin called - player_id: {player_id}, skin: {skin_name}")

            if not player_id or not skin_name:
                return JsonResponse({
                    'success': False,
                    'error': 'Не указаны player_id или skin_name'
                })

            player = Player.objects.get(id=player_id)

            # Список доступных скинов
            available_skins = [
                'cat.png',
                'skin3.png',
                'skin4.png',
                'skin5.png',
                'skin6.png',
                'skin7.png',
                'skin8.png'
            ]

            # Проверяем существование файла скина
            import os
            from django.conf import settings

            # Пути для проверки
            possible_paths = [
                os.path.join(settings.BASE_DIR, 'main', 'static', 'main', 'skins', skin_name),
                os.path.join(settings.BASE_DIR, 'static', 'main', 'skins', skin_name),
            ]

            skin_exists = False
            for skin_path in possible_paths:
                if os.path.exists(skin_path):
                    skin_exists = True
                    print(f"DEBUG: Skin found at {skin_path}")
                    break

            # Если файл существует в доступных скинах
            if skin_name in available_skins and skin_exists:
                player.current_skin = skin_name
                player.save()
                print(f"DEBUG: Skin updated to {skin_name} for player {player_id}")

                return JsonResponse({
                    'success': True,
                    'current_skin': skin_name,
                    'message': f'Скин изменен на {skin_name}'
                })
            else:
                print(f"DEBUG: Skin {skin_name} not available. Available: {available_skins}")
                return JsonResponse({
                    'success': False,
                    'error': f'Скин {skin_name} не найден или недоступен'
                })

        except Player.DoesNotExist:
            print(f"DEBUG: Player {player_id} not found")
            return JsonResponse({
                'success': False,
                'error': 'Игрок не найден'
            })
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Неверный формат JSON'
            })
        except Exception as e:
            print(f"DEBUG: Unexpected error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({
        'success': False,
        'error': 'Неверный метод запроса'
    })

# views.py - добавить если нет
def get_skins_list_simple():
    """Упрощенная функция получения списка скинов"""
    return ['cat.png', 'skin3.png', 'skin4.png', 'skin5.png',
            'skin6.png', 'skin7.png', 'skin8.png']


@csrf_protect
def buy_box(request):
    """Покупка ящика"""
    print(f"DEBUG: buy_box called, method: {request.method}")
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            box_id = data.get('box_id')
            print(f"DEBUG: box_id = {box_id}")
            
            # Получаем игрока (авторизованного или анонимного)
            if request.user.is_authenticated:
                try:
                    player = Player.objects.get(user=request.user)
                    print(f"DEBUG: Авторизованный игрок найден: {player.id}, монеты: {player.coins}")
                except Player.DoesNotExist:
                    print("DEBUG: Профиль авторизованного игрока не найден")
                    return JsonResponse({'success': False, 'error': 'Профиль игрока не найден'})
            else:
                # Для анонимных пользователей используем сессию
                player_id = request.session.get('player_id')
                print(f"DEBUG: Анонимный пользователь, player_id из сессии: {player_id}")
                if not player_id:
                    print("DEBUG: player_id не найден в сессии")
                    return JsonResponse({'success': False, 'error': 'Игрок не найден'})
                try:
                    player = Player.objects.get(id=player_id)
                    print(f"DEBUG: Анонимный игрок найден: {player.id}, монеты: {player.coins}")
                except Player.DoesNotExist:
                    print(f"DEBUG: Игрок с ID {player_id} не найден в базе")
                    return JsonResponse({'success': False, 'error': 'Игрок не найден'})
            
            try:
                box = Box.objects.get(id=box_id, is_active=True)
                print(f"DEBUG: Ящик найден: {box.name}, цена: {box.price}")
            except Box.DoesNotExist:
                print(f"DEBUG: Ящик с ID {box_id} не найден")
                return JsonResponse({'success': False, 'error': 'Ящик не найден'})
            
            if player.coins >= box.price:
                print(f"DEBUG: У игрока достаточно монет ({player.coins} >= {box.price})")
                player.coins -= box.price
                player.save()
                print(f"DEBUG: Монеты списаны, осталось: {player.coins}")
                
                # Открываем ящик и получаем предмет
                result = open_box(player, box)
                print(f"DEBUG: Результат открытия ящика: {result}")
                
                return JsonResponse({
                    'success': True,
                    'coins': player.coins,
                    'result': result
                })
            else:
                print(f"DEBUG: Недостаточно монет ({player.coins} < {box.price})")
                return JsonResponse({
                    'success': False,
                    'error': f'Недостаточно монет. Нужно: {box.price}'
                })
                
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")
            return JsonResponse({'success': False, 'error': 'Неверный формат данных'})
        except (Player.DoesNotExist, Box.DoesNotExist) as e:
            print(f"DEBUG: Object not found: {e}")
            return JsonResponse({'success': False, 'error': 'Не найдено'})
        except Exception as e:
            print(f"DEBUG: Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    print(f"DEBUG: Неверный метод запроса: {request.method}")
    return JsonResponse({'success': False, 'error': 'Неверный метод'})


def open_box(player, box):
    """Открыть ящик и получить случайный предмет"""
    drops = list(box.drops.all())
    if not drops:
        return {'error': 'Ящик пуст'}
    
    # Генерируем случайное число от 0 до 100
    rand = random.uniform(0, 100)
    cumulative_chance = 0
    
    # Сортируем дропы по убыванию шанса для корректной работы
    drops = sorted(drops, key=lambda x: x.drop_chance, reverse=True)
    
    for drop in drops:
        cumulative_chance += drop.drop_chance
        if rand <= cumulative_chance:
            # Применяем награду
            if drop.item_type == 'skin':
                unlocked = player.unlock_skin_from_box(drop.item_value)
                if unlocked:
                    message = f'Получен новый скин: {drop.item_value}'
                else:
                    # Если скин уже есть, даем монеты
                    coins_reward = 50
                    player.coins += coins_reward
                    player.save()
                    message = f'Скин уже есть! Получено {coins_reward} монет'
            elif drop.item_type == 'coins':
                coins_amount = int(drop.item_value)
                player.coins += coins_amount
                player.save()
                message = f'Получено {coins_amount} монет'
            elif drop.item_type == 'clicks':
                clicks_amount = int(drop.item_value)
                player.clicks += clicks_amount
                player.save()
                message = f'Получено {clicks_amount} кликов'
            
            # Сохраняем историю
            BoxOpening.objects.create(
                player=player,
                box=box,
                item_type=drop.item_type,
                item_value=drop.item_value,
                is_rare=drop.is_rare
            )
            
            return {
                'item_type': drop.item_type,
                'item_value': drop.item_value,
                'is_rare': drop.is_rare,
                'message': message
            }
    
    # Если ничего не выпало, возвращаем первый предмет (гарантированный дроп)
    first_drop = drops[0]
    if first_drop.item_type == 'coins':
        coins_amount = int(first_drop.item_value)
        player.coins += coins_amount
        player.save()
        message = f'Получено {coins_amount} монет'
    elif first_drop.item_type == 'clicks':
        clicks_amount = int(first_drop.item_value)
        player.clicks += clicks_amount
        player.save()
        message = f'Получено {clicks_amount} кликов'
    else:
        unlocked = player.unlock_skin_from_box(first_drop.item_value)
        if unlocked:
            message = f'Получен новый скин: {first_drop.item_value}'
        else:
            coins_reward = 50
            player.coins += coins_reward
            player.save()
            message = f'Скин уже есть! Получено {coins_reward} монет'
    
    BoxOpening.objects.create(
        player=player,
        box=box,
        item_type=first_drop.item_type,
        item_value=first_drop.item_value,
        is_rare=first_drop.is_rare
    )
    
    return {
        'item_type': first_drop.item_type,
        'item_value': first_drop.item_value,
        'is_rare': first_drop.is_rare,
        'message': message
    }


@csrf_protect
@login_required
def unlock_skin(request):
    """Разблокировка скина"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            skin_name = data.get('skin_name')
            
            player = Player.objects.get(user=request.user)
            
            # Получаем скин из базы данных
            try:
                skin = Skin.objects.get(image_name=skin_name)
            except Skin.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Скин не найден'
                })
            
            # Проверяем, может ли игрок разблокировать скин
            can_unlock = (player.clicks >= skin.required_clicks and 
                         player.coins >= skin.price)
            if can_unlock:
                # Проверяем, достаточно ли монет
                if player.coins >= skin.price:
                    # Списываем монеты
                    if skin.price > 0:
                        player.coins -= skin.price
                        player.save()
                    
                    # Разблокируем скин
                    PlayerSkin.objects.get_or_create(
                        player=player,
                        skin=skin,
                        defaults={'unlocked_at': timezone.now()}
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Скин {skin.name} разблокирован!',
                        'new_coins': player.coins
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': f'Недостаточно монет. Нужно: {skin.price}'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Не выполнены требования для разблокировки. Нужно {skin.required_clicks} кликов'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Неверный метод запроса'
    })

