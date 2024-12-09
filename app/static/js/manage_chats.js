$(document).ready(function () {
    const token = localStorage.getItem('access_token');

    // Если токен отсутствует, перенаправляем на домашнюю страницу
    if (!token) {
        console.warn('JWT токен отсутствует. Перенаправление на главную страницу.');
        window.location.href = '/';
    } else {
        // Проверка валидности токена на сервере
        $.ajax({
            url: '/protected',
            type: 'GET',
            headers: {
                Authorization: 'Bearer ' + token,
            },
            success: function (response) {
                loadPrompts();
                loadChats();
                console.log('Токен валидный, пользователь: ', response.logged_in_as);
            },
            error: function (xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                window.location.href = '/';
            },
        });
    }

    function showError(message) {
        $('#error').text(message).show();
    }

    function loadChats() {
        $.ajax({
            url: '/api/chats',
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: function (chats) {
                console.log('Загруженные чаты:', chats); // Логируем чаты
                renderChats(chats);
            },
            error: function () {
                showError('Ошибка загрузки чатов.');
            },
        });
    }

    function loadPrompts() {
        $.ajax({
            url: '/api/prompts',
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: function (prompts) {
                console.log('Загруженные промпты:', prompts); // Логируем промпты
                window.prompts = prompts; // Сохраняем промпты в глобальную переменную
            },
            error: function () {
                showError('Ошибка загрузки промптов.');
            },
        });
    }

    function renderChats(chats) {
        const chatTable = $('#chatTable');
        chatTable.empty();

        chats.forEach(chat => {
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
                window.prompts.forEach(prompt => {
                    promptSelect.append(`
                        <option value="${prompt.prompt_id}" ${chat.default_prompt_id === prompt.prompt_id ? 'selected' : ''}>
                            ${prompt.prompt_name}
                        </option>
                    `);
                });
            }

            chatTable.append(chatRow);
        });

        $('.save-prompt-btn').on('click', function () {
            const chatId = $(this).data('chat-id');
            const promptId = $(`.prompt-select[data-chat-id="${chatId}"]`).val();

            if (!promptId) {
                alert('Пожалуйста, выберите промпт.');
                return;
            }

            savePrompt(chatId, promptId);
        });

        $('#content').show();
    }

    function savePrompt(chatId, promptId) {
        $.ajax({
            url: '/update_chat_prompt',
            type: 'POST',
            contentType: 'application/json',
            headers: { Authorization: `Bearer ${token}` },
            data: JSON.stringify({ chat_id: chatId, prompt_id: promptId }),
            success: function () {
                alert('Дефолтный промпт успешно обновлён!');
            },
            error: function (xhr) {
                alert(xhr.responseJSON.error || 'Ошибка при обновлении промпта.');
            },
        });
    }
});
