// achievements.js
let playerId = null;

document.addEventListener('DOMContentLoaded', function() {
    // Получаем playerId
    const playerIdElement = document.getElementById('player-id');
    if (playerIdElement && playerIdElement.value) {
        playerId = playerIdElement.value;
    }
});

function checkForNewAchievements() {
    if (!playerId) return;

    fetch('/achievements/check/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.new_achievements.length > 0) {
            // Показываем попап для каждого нового достижения
            data.new_achievements.forEach(achievement => {
                showAchievementPopup(achievement);
            });

            // Обновляем страницу, если мы на странице достижений
            if (window.location.pathname.includes('achievements')) {
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            }
        }
    })
    .catch(error => console.error('Error checking achievements:', error));
}

function showAchievementPopup(achievement) {
    const popup = document.getElementById('achievement-popup');
    const nameElement = document.getElementById('popup-achievement-name');
    const descElement = document.getElementById('popup-achievement-desc');
    const rewardsElement = document.getElementById('popup-achievement-rewards');

    // Устанавливаем цвета в зависимости от редкости
    const rarityColors = {
        'common': '#808080',
        'uncommon': '#1EFF00',
        'rare': '#0070DD',
        'epic': '#A335EE',
        'legendary': '#FF8000'
    };

    popup.style.borderColor = rarityColors[achievement.rarity] || '#FFD700';
    popup.querySelector('.popup-icon i').className = achievement.icon;
    popup.querySelector('.popup-icon').style.color = rarityColors[achievement.rarity] || '#FFD700';

    nameElement.textContent = achievement.name;
    descElement.textContent = achievement.description;

    // Очищаем и добавляем награды
    rewardsElement.innerHTML = '';
    if (achievement.reward_coins > 0) {
        const reward = document.createElement('div');
        reward.className = 'reward-item';
        reward.innerHTML = `<i class="fas fa-coins"></i> +${achievement.reward_coins} монет`;
        rewardsElement.appendChild(reward);
    }

    // Показываем попап
    popup.classList.add('show');

    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        if (popup.classList.contains('show')) {
            closeAchievementPopup();
            markAchievementSeen(achievement.id);
        }
    }, 5000);
}

function closeAchievementPopup() {
    const popup = document.getElementById('achievement-popup');
    popup.classList.remove('show');
}

function markAchievementSeen(achievementId) {
    fetch(`/achievements/${achievementId}/mark_seen/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Удаляем карточку достижения или убираем метку "NEW"
            const card = document.querySelector(`[data-achievement-id="${achievementId}"]`);
            if (card) {
                card.classList.remove('new-unlocked');
                const newBadge = card.querySelector('.new-badge');
                if (newBadge) newBadge.remove();
                const markBtn = card.querySelector('.mark-seen-btn');
                if (markBtn) markBtn.remove();
            }
        }
    })
    .catch(error => console.error('Error marking achievement seen:', error));
}

function loadNextAchievements() {
    fetch('/achievements/progress/', {
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.next_achievements.length > 0) {
            const container = document.querySelector('.next-achievements');
            if (container) {
                container.innerHTML = '';

                data.next_achievements.forEach(item => {
                    const achievementDiv = document.createElement('div');
                    achievementDiv.className = 'next-achievement';

                    achievementDiv.innerHTML = `
                        <div class="next-icon">
                            <i class="${item.icon}"></i>
                        </div>
                        <div class="next-info">
                            <h5>${item.name}</h5>
                            <div class="next-progress">
                                <div class="progress-bar">
                                    <div class="progress-fill"
                                         style="width: ${item.progress.percentage}%"></div>
                                </div>
                                <span>${Math.round(item.progress.percentage)}%</span>
                            </div>
                        </div>
                    `;

                    container.appendChild(achievementDiv);
                });
            }
        }
    })
    .catch(error => console.error('Error loading next achievements:', error));
}

// Вспомогательная функция для получения CSRF токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// achievements.js - добавьте эти функции для анимаций

function animateAchievementCard(card) {
    // Добавляем анимацию для карточки
    card.style.animation = 'new-card-float 3s infinite ease-in-out';

    // Добавляем эффект свечения
    card.style.boxShadow = '0 0 40px rgba(255, 215, 0, 0.8)';

    // Через 5 секунд убираем анимацию
    setTimeout(() => {
        card.style.animation = '';
        card.style.boxShadow = '';
    }, 5000);
}

function addRarityGlow(card, rarity) {
    // Добавляем свечение в зависимости от редкости
    const glowColors = {
        'common': 'rgba(128, 128, 128, 0.5)',
        'uncommon': 'rgba(30, 255, 0, 0.5)',
        'rare': 'rgba(0, 112, 221, 0.5)',
        'epic': 'rgba(163, 53, 238, 0.5)',
        'legendary': 'rgba(255, 128, 0, 0.7)'
    };

    card.style.boxShadow = `0 0 30px ${glowColors[rarity] || glowColors.common}`;
}

// При загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем анимацию для новых достижений
    const newAchievements = document.querySelectorAll('.new-unlocked');
    newAchievements.forEach(card => {
        const rarity = card.classList[1].replace('rarity-', '');
        addRarityGlow(card, rarity);
        animateAchievementCard(card);
    });

    // Добавляем hover эффекты для всех карточек
    const allCards = document.querySelectorAll('.achievement-card');
    allCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const rarity = this.classList[1]?.replace('rarity-', '') || 'common';
            addRarityGlow(this, rarity);
        });

        card.addEventListener('mouseleave', function() {
            if (!this.classList.contains('new-unlocked')) {
                this.style.boxShadow = '';
            }
        });
    });

    // Запускаем проверку достижений
    checkForNewAchievements();
    loadNextAchievements();

    // Автоматическая проверка каждые 30 секунд
    setInterval(checkForNewAchievements, 30000);
});

// Остальные функции (showAchievementPopup, markAchievementSeen и т.д.)
// остаются без изменений...