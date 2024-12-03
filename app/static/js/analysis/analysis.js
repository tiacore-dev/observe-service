$(document).ready(function () {
    const token = localStorage.getItem('access_token');
    let filteredMessages = []; // Хранение сообщений после фильтрации
    let defaultPromptId = null; // Хранение ID автоматического промпта

    if (!token) {
        window.location.href = '/';
    } else {
        $.ajax({
            url: '/protected',
            type: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            success: function () {
                loadPrompts().then(() => {
                    checkAutomaticPrompt(); // Проверяем автоматический промпт только после загрузки промптов
                });
            },
            error: function () {
                window.location.href = '/';
            }
        });
    }

    // Настройка диапазона дат
    $('#date_range').daterangepicker({
        locale: { format: 'YYYY-MM-DD', separator: ' до ' },
        opens: 'left',
    });

    function loadPrompts() {
        return $.ajax({
            url: '/user_prompts',
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: function (response) {
                const promptSelect = $('#prompt_name');
                promptSelect.empty(); // Очищаем список перед добавлением новых данных
                promptSelect.append('<option value="">-- Выберите промпт --</option>'); // Добавляем опцию по умолчанию

                response.prompt_data.forEach(prompt => {
                    promptSelect.append(`<option value="${prompt.prompt_id}">${prompt.prompt_name}</option>`);
                });

                // Если автоматический промпт уже найден, выбираем его
                if (defaultPromptId) {
                    promptSelect.val(defaultPromptId);
                }
            },
            error: function () {
                alert('Ошибка при загрузке промптов.');
            },
        });
    }

    function checkAutomaticPrompt() {
        return $.ajax({
            url: '/get_automatic_prompt',
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function (response) {
                if (response.prompt_id) {
                    defaultPromptId = response.prompt_id; // Сохраняем ID автоматического промпта
                    $('#prompt_name').val(response.prompt_id); // Устанавливаем как выбранный
                }
            },
            error: function () {
                console.log('Ошибка получения автоматического промпта.');
            }
        });
    }

    // Фильтрация сообщений
    $('#filterButton').on('click', function () {
        const [start_date, end_date] = $('#date_range').val().split(' до ');
        const user_id = $('#user_id').val();
        const chat_id = $('#chat_id').val();

        let url = '/api/messages?';
        if (start_date) url += `start_date=${start_date}&`;
        if (end_date) url += `end_date=${end_date}&`;
        if (user_id) url += `user_id=${user_id}&`;
        if (chat_id) url += `chat_id=${chat_id}`;

        $('#loadingIcon').show();
        $.ajax({
            url,
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: (data) => {
                $('#loadingIcon').hide();
                $('#messageSummary').show().find('#messageCount').text(data.length);
                filteredMessages = data; // Сохраняем отфильтрованные сообщения
            },
            error: () => {
                $('#loadingIcon').hide();
                alert('Ошибка при загрузке сообщений.');
            },
        });
    });

    // Запуск анализа
    $('#submitButton').on('click', function () {
        const dateRange = $('#date_range').val().split(' до ');
        const start_date = dateRange[0];
        const end_date = dateRange[1];
        const user_id = $('#user_id').val();
        const chat_id = $('#chat_id').val();
        const prompt_id = $('#prompt_name').val();

        if (!prompt_id) {
            alert('Пожалуйста, выберите промпт.');
            return;
        }

        if (filteredMessages.length === 0) {
            alert('Сначала выполните фильтрацию сообщений.');
            return;
        }

        const filters = {
            start_date: start_date || null,
            end_date: end_date || null,
            user_id: user_id || null,
            chat_id: chat_id || null,
        };

        $('#loadingIcon').show();
        $.ajax({
            url: '/analysis/create',
            type: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            contentType: 'application/json',
            data: JSON.stringify({ prompt_id, filters, messages: filteredMessages }),
            success: function () {
                $('#loadingIcon').hide();
                alert('Анализ успешно создан!');
                window.location.href = '/analysis_result';
            },
            error: function () {
                $('#loadingIcon').hide();
                alert('Ошибка при создании анализа.');
            },
        });
    });
});
