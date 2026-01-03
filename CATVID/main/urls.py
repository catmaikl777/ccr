from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('click/', views.click, name='click'),
    path('buy_upgrade/', views.buy_upgrade, name='buy_upgrade'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('test/', views.test_click, name='test_click'),
    path('test-boxes/', lambda request: render(request, 'main/test_boxes.html'), name='test_boxes'),
    path('sound-test/', views.sound_test_view, name='sound_test'),
    path('auto_click/', views.auto_click, name='auto_click'),
    path('player/<int:player_id>/auto_clicker'
         '_info/', views.get_auto_clicker_info, name='auto_clicker_info'),
    path('skins/', views.skins_view, name='skins'),
    path('change_skin/', views.change_skin, name='change_skin'),
    path('update_skin/', views.update_skin, name='update_skin'),
    path('player/<int:player_id>/current_skin/', views.get_current_skin, name='get_current_skin'),
    path('achievements/', views.achievements_view, name='achievements'),
    path('achievements/check/', views.check_achievements, name='check_achievements'),
    path('achievements/<int:achievement_id>/mark_seen/', views.mark_achievement_seen, name='mark_achievement_seen'),
    path('achievements/progress/', views.get_achievement_progress, name='get_achievement_progress'),
    path('buy_box/', views.buy_box, name='buy_box'),
    path('unlock_skin/', views.unlock_skin, name='unlock_skin'),
]
#     path('create/', views.create_battle_view, name='create_battle'),
#     path('find/', views.find_opponent_view, name='find_opponent'),
#     path('battle/<int:battle_id>/', views.battle_room_view, name='battle_room'),
#     path('results/<int:battle_id>/', views.battle_results_view, name='battle_results'),
#     path('history/', views.battle_history_view, name='history'),
#
#     # API endpoints
#     path('api/create/', views.api_create_battle, name='api_create_battle'),
#     path('api/find/', views.api_find_opponent, name='api_find_opponent'),
#     path('api/<int:battle_id>/click/', views.api_register_click, name='api_register_click'),
#     path('api/<int:battle_id>/updates/', views.api_get_updates, name='api_get_updates'),
#     path('api/<int:battle_id>/ready/', views.api_set_ready, name='api_set_ready'),
#     path('api/<int:battle_id>/status/', views.api_battle_status, name='api_battle_status'),
#     path('api/<int:battle_id>/surrender/', views.api_surrender, name='api_surrender'),
#     path('api/list/', views.api_battle_list, name='api_battle_list'),
#     path('api/stats/', views.api_user_stats, name='api_user_stats'),
#
#     # Приглашения
#     path('invites/', views.invites_view, name='invites'),
#     path('api/invite/send/', views.api_send_invite, name='api_send_invite'),
#     path('api/invite/<int:invite_id>/accept/', views.api_accept_invite, name='api_accept_invite'),
#     path('api/invite/<int:invite_id>/reject/', views.api_reject_invite, name='api_reject_invite'),
#     path('api/invites/list/', views.api_invites_list, name='api_invites_list'),
# ]