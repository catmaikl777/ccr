class BattleManager {
    constructor(battleId, userId) {
        this.battleId = battleId;
        this.userId = userId;
        this.isPolling = false;
        this.lastHash = '';
    }

    // Long Polling для обновлений
    async pollUpdates() {
        if (this.isPolling) return;

        this.isPolling = true;
        try {
            const response = await fetch(`/api/battle/${this.battleId}/updates/?last_check=${this.lastHash}`);
            const data = await response.json();

            if (data.has_update) {
                this.lastHash = data.hash;
                this.updateUI(data.data);

                // Если баттл завершен
                if (data.data.status === 'finished') {
                    this.showResults(data.data);
                    return;
                }
            }

            // Если таймаут или нет обновлений, запускаем снова
            if (!data.timeout || data.has_update) {
                setTimeout(() => {
                    this.isPolling = false;
                    this.pollUpdates();
                }, 100);
            }
        } catch (error) {
            console.error('Polling error:', error);
            this.isPolling = false;
            setTimeout(() => this.pollUpdates(), 1000);
        }
    }

    // Отправка клика
    async sendClick() {
        try {
            const response = await fetch(`/api/battle/${this.battleId}/click/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Click error:', error);
        }
    }
}