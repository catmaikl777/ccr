// Система открытия ящиков в стиле Brawl Stars
class BrawlBoxOpening {
    constructor() {
        this.isOpening = false;
    }

    async openBox(boxId, price, button) {
        if (this.isOpening) return;

        const originalText = button.innerHTML;
        const originalDisabled = button.disabled;

        // Блокируем кнопку на время открытия
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Открываем...';
        button.disabled = true;
        button.style.opacity = '0.7';

        this.isOpening = true;

        try {
            const response = await fetch('/buy_box/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ box_id: boxId })
            });

            const data = await response.json();

            if (data.success) {
                // Обновляем баланс
                if (window.gameState) {
                    window.gameState.coins = data.coins;
                    document.getElementById('coins').textContent = data.coins.toLocaleString();
                }

                // Показываем уведомление с результатом
                this.showSimpleNotification(data.result);

                // Обновляем скин, если получен
                if (data.result.item_type === 'skin' && window.gameState) {
                    window.gameState.currentSkin = data.result.item_value;
                    const skinImg = document.getElementById('skin-image');
                    if (skinImg) {
                        skinImg.src = `/static/main/skins/${data.result.item_value}`;
                        // Эффект смены скина
                        skinImg.style.transform = 'scale(1.1)';
                        setTimeout(() => {
                            skinImg.style.transform = 'scale(1)';
                        }, 200);
                    }
                }

                // Обновляем кнопку ящика
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.disabled = originalDisabled;
                    button.style.opacity = '1';
                }, 1000);
            } else {
                this.showError(data.error || 'Ошибка открытия ящика');
                button.innerHTML = originalText;
                button.disabled = originalDisabled;
                button.style.opacity = '1';
            }
        } catch (error) {
            this.showError('Ошибка сети: ' + error.message);
            button.innerHTML = originalText;
            button.disabled = originalDisabled;
            button.style.opacity = '1';
        } finally {
            this.isOpening = false;
        }
    }

    // Простое уведомление сверху
    showSimpleNotification(result) {
        // Создаем контейнер для уведомлений, если его нет
        let notificationsContainer = document.getElementById('notifications-container');
        if (!notificationsContainer) {
            notificationsContainer = document.createElement('div');
            notificationsContainer.id = 'notifications-container';
            notificationsContainer.style.cssText = `
                position: fixed;
                top: 20px;
                left: 0;
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 10px;
                z-index: 100000;
                pointer-events: none;
            `;
            document.body.appendChild(notificationsContainer);
        }

        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = 'top-notification';
        notification.dataset.type = result.item_type;
        notification.dataset.rare = result.is_rare ? 'true' : 'false';

        // Иконка в зависимости от типа награды
        let iconClass = '';
        let iconColor = '';
        switch(result.item_type) {
            case 'skin':
                iconClass = 'fas fa-palette';
                iconColor = '#9c88ff';
                break;
            case 'coins':
                iconClass = 'fas fa-coins';
                iconColor = '#fdcb6e';
                break;
            case 'clicks':
                iconClass = 'fas fa-mouse-pointer';
                iconColor = '#00b894';
                break;
        }

        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">
                    <i class="${iconClass}"></i>
                </div>
                <div class="notification-text">
                    <strong>${result.message}</strong>
                    <span>${result.item_value}</span>
                    ${result.is_rare ? '<span class="rare-tag">Редкий!</span>' : ''}
                </div>
            </div>
        `;

        // Добавляем уведомление в контейнер
        notificationsContainer.appendChild(notification);

        // Анимация появления
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Автоматическое скрытие через 4 секунды
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                // Удаляем контейнер, если уведомлений больше нет
                if (notificationsContainer.children.length === 0) {
                    notificationsContainer.remove();
                }
            }, 300);
        }, 4000);

        // Закрытие по клику
        notification.style.pointerEvents = 'auto';
        notification.addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                if (notificationsContainer.children.length === 0) {
                    notificationsContainer.remove();
                }
            }, 300);
        });
    }

    showError(message) {
        // Создаем контейнер для ошибок, если его нет
        let errorsContainer = document.getElementById('errors-container');
        if (!errorsContainer) {
            errorsContainer = document.createElement('div');
            errorsContainer.id = 'errors-container';
            errorsContainer.style.cssText = `
                position: fixed;
                top: 20px;
                left: 0;
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 10px;
                z-index: 100001;
                pointer-events: none;
            `;
            document.body.appendChild(errorsContainer);
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'top-error';
        errorDiv.innerHTML = `
            <div class="error-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
            </div>
        `;

        errorsContainer.appendChild(errorDiv);

        // Анимация появления
        setTimeout(() => {
            errorDiv.classList.add('show');
        }, 10);

        // Автоматическое скрытие через 3 секунды
        setTimeout(() => {
            errorDiv.classList.remove('show');
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.parentNode.removeChild(errorDiv);
                }
                if (errorsContainer.children.length === 0) {
                    errorsContainer.remove();
                }
            }, 300);
        }, 3000);

        // Закрытие по клику
        errorDiv.style.pointerEvents = 'auto';
        errorDiv.addEventListener('click', () => {
            errorDiv.classList.remove('show');
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.parentNode.removeChild(errorDiv);
                }
                if (errorsContainer.children.length === 0) {
                    errorsContainer.remove();
                }
            }, 300);
        });
    }

    getCookie(name) {
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
}

window.boxOpening = new BrawlBoxOpening();