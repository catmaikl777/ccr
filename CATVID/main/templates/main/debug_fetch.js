console.log('=== Debug Fetch Override ===');

// Сохраняем оригинальную функцию fetch
const originalFetch = window.fetch;

// Перехватываем все вызовы fetch
window.fetch = function(...args) {
    console.log('=== Fetch called ===');
    console.log('URL:', args[0]);
    console.log('Options:', args[1]);
    console.log('Stack:', new Error().stack);
    
    // Выводим содержимое тела запроса, если есть
    if (args[1] && args[1].body) {
        try {
            const body = args[1].body;
            if (typeof body === 'string') {
                console.log('Request body:', JSON.parse(body));
            } else {
                console.log('Request body (non-string):', body);
            }
        } catch (e) {
            console.log('Could not parse request body:', body);
        }
    }
    
    // Вызываем оригинальный fetch
    return originalFetch.apply(this, args)
        .then(response => {
            console.log('=== Fetch response ===');
            console.log('Status:', response.status);
            console.log('URL:', response.url);
            
            // Клонируем ответ для чтения тела
            const responseClone = response.clone();
            responseClone.text().then(text => {
                try {
                    console.log('Response JSON:', JSON.parse(text));
                } catch (e) {
                    console.log('Response text:', text);
                }
            }).catch(err => {
                console.log('Could not read response:', err);
            });
            
            return response;
        })
        .catch(error => {
            console.log('=== Fetch error ===');
            console.log('Error:', error);
            console.log('Error name:', error.name);
            console.log('Error message:', error.message);
            console.log('Stack:', error.stack);
            throw error;
        });
};

console.log('Fetch override installed');