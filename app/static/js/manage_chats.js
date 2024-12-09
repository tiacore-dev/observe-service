$(document).ready(function () {
    const token = localStorage.getItem('access_token');
    let promptsLoaded = false;
    let chatsLoaded = false;
    let chatsData = [];

    if (!token) {
        console.warn('JWT токен отсутствует. Перенаправление на главную страницу.');
        window.location.href = '/';
    } else {
        console.log('Токен найден, проверяем его валидность...');
        // Проверка валидности токена на сервере
        $.ajax({
            url: '/protected',
            type: 'GET',
            headers: {
                Authorization: 'Bearer ' + token,
            },
            success: function (response) {
                console.log('Токен валиден, пользователь:', response.logged_in_as);
                console.log('Загружаем промпты и чаты...');
                loadPrompts();
                loadChats();
            },
            error: function (xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                console.warn('Перенаправляем на главную страницу...');
                window.location.href = '/';
            },
        });
    }

    function showError(message) {
        console.error('Ошибка:', message);
        $('#error').text(message).show();
    }

    function loadChats() {
        console.log('Запрашиваем список чатов...');
        $.ajax({
            url: '/api/chats',
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: function (chats) {
                console.log('Список чатов успешно загружен:', chats);
                chatsData = chats; // Сохраняем данные чатов
                chatsLoaded = true;
                checkAndRender();
            },
            error: function () {
                showError('Ошибка загрузки чатов.');
            },
        });
    }

    function loadPrompts() {
        console.log('Запрашиваем список промптов...');
        $.ajax({
            url: '/api/prompts',
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: function (prompts) {
                console.log('Список промптов успешно загружен:', prompts);
                window.prompts = prompts; // Сохраняем промпты в глобальную переменную
                promptsLoaded = true;
                checkAndRender();
            },
            error: function () {
                showError('Ошибка загрузки промптов.');
            },
        });
    }

    function checkAndRender() {
        if (promptsLoaded && chatsLoaded) {
            renderChats(chatsData);
        }
    }

    function renderChats(chats) {
        console.log('Рендерим таблицу чатов...');
        const chatTable = $('#chatTable');
        chatTable.empty();

        chats.forEach(chat => {
            console.log(`Рендерим чат: ${chat.chat_id} (${chat.chat_name || 'Без имени'})`);
            const chatRow = $(`
                <tr>
                    <td>${chat.chat_id}</td>
                    <td>${chat.chat_name || 'Без имени'}</td>
                    <td>
                        <select class="form-select prompt-select" data-chat-id="${chat.chat_id}">
                            <option value="">-- Выберите промпт --</option>
                        </select>
                    </td>
                    <td>
                        <button class="btn btn-primary save-prompt-btn" data-chat-id="${chat.chat_id}">Сохранить</button>
                    </td>
                </tr>
            `);

            const promptSelect = chatRow.find('.prompt-select');
            if (window.prompts) {
                console.log(`Добавляем промпты для чата ${chat.chat_id}...`);
                window.prompts.forEach(prompt => {
                    console.log(`Добавляем промпт: ${prompt.prompt_name} (ID: ${prompt.prompt_id})`);
                    promptSelect.append(`
                        <option value="${prompt.prompt_id}" ${chat.default_prompt_id === prompt.prompt_id ? 'selected' : ''}>
                            ${prompt.prompt_name}
                        </option>
                    `);
                });
            } else {
                console.warn('Список промптов не загружен или пуст.');
            }

            chatTable.append(chatRow);
        });

        $('.save-prompt-btn').on('click', function () {
            const chatId = $(this).data('chat-id');
            const promptId = $(`.prompt-select[data-chat-id="${chatId}"]`).val();
            console.log(`Нажата кнопка сохранения для чата ${chatId}. Выбран промпт: ${promptId}`);

            if (!promptId) {
                alert('Пожалуйста, выберите промпт.');
                console.warn('Сохранение отменено: промпт не выбран.');
                return;
            }

            savePrompt(chatId, promptId);
        });

        console.log('Отображаем содержимое страницы...');
        $('#content').show();
    }

    function savePrompt(chatId, promptId) {
        console.log(`Сохраняем промпт ${promptId} для чата ${chatId}...`);
        $.ajax({
            url: '/update_chat_prompt',
            type: 'POST',
            contentType: 'application/json',
            headers: { Authorization: `Bearer ${token}` },
            data: JSON.stringify({ chat_id: chatId, prompt_id: promptId }),
            success: function () {
                console.log(`Дефолтный промпт для чата ${chatId} успешно обновлён на ${promptId}`);
                alert('Дефолтный промпт успешно обновлён!');
            },
            error: function (xhr) {
                console.error('Ошибка при обновлении промпта:', xhr.responseJSON.error);
                alert(xhr.responseJSON.error || 'Ошибка при обновлении промпта.');
            },
        });
    }
});
