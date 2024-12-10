$(document).ready(function () {
    const token = localStorage.getItem('access_token');
    let filteredMessages = []; // Хранение сообщений после фильтрации
    let defaultPromptId = null; // Хранение ID автоматического промпта
    let prompts = []; // Список всех промптов

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
                loadChats();
                loadUsers();
            },
            error: function () {
                window.location.href = '/';
            }
        });
    }

    // Настройка диапазона дат
    $('#start_date').daterangepicker({
        singleDatePicker: true,
        autoApply: true, // Автоматическое применение при выборе
        locale: { format: 'DD-MM-YYYY' } // Формат отображения для пользователя
    });
    
    $('#end_date').daterangepicker({
        singleDatePicker: true,
        autoApply: true, // Автоматическое применение при выборе
        locale: { format: 'DD-MM-YYYY' } // Формат отображения для пользователя
    });
    
    
    

    function loadPrompts() {
        return $.ajax({
            url: '/user_prompts',
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: function (response) {
                prompts = response.prompt_data;
                const promptSelect = $('#prompt_name');
                promptSelect.empty();
                promptSelect.append('<option value="">-- Выберите промпт --</option>');

                prompts.forEach(prompt => {
                    promptSelect.append(`<option value="${prompt.prompt_id}">${prompt.prompt_name}</option>`);
                });
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
                Authorization: 'Bearer ' + token,
            },
            success: function (response) {
                if (response.prompt_id) {
                    defaultPromptId = response.prompt_id;
                    $('#prompt_name').val(defaultPromptId); // Устанавливаем основной дефолтный промпт
                }
            },
            error: function () {
                console.log('Ошибка получения автоматического промпта.');
            },
        });
    }

    let currentPage = 1;
    const messagesPerPage = 10;
    
    function displayMessages(messages) {
        // Проверка: messages должен быть массивом
        if (!Array.isArray(messages)) {
            console.error('Ошибка: Ожидается массив сообщений.');
            return;
        }
    
        const start = (currentPage - 1) * messagesPerPage;
        const end = start + messagesPerPage;
        const paginatedMessages = messages.slice(start, end);
    
        const messagesList = $('#messagesList');
        messagesList.empty(); // Очищаем список перед добавлением новых сообщений
    
        if (paginatedMessages.length === 0) {
            messagesList.append('<p class="text-muted">Сообщений не найдено.</p>');
            return;
        }
    
        const table = $(`
            <table class="table table-sm table-striped table-bordered">
                <thead class="table-light">
                    <tr>
                        <th>Дата и время</th>
                        <th>User ID</th>
                        <th>Chat ID</th>
                        <th>Сообщение</th>
                        <th>S3 Key</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        `);
    
        paginatedMessages.forEach(msg => {
            const date = msg.timestamp ? moment(msg.timestamp).format('DD-MM-YYYY HH:mm:ss') : 'Не указано';
            const userId = msg.user_id || 'Не указано';
            const chatId = msg.chat_id || 'Не указано';
            const text = msg.text || 'Пустое сообщение';
            const s3Key = msg.s3_key || 'Не указано';
    
            table.find('tbody').append(`
                <tr>
                    <td>${date}</td>
                    <td>${userId}</td>
                    <td>${chatId}</td>
                    <td>${text}</td>
                    <td>${s3Key}</td>
                </tr>
            `);
        });
    
        messagesList.append(table);
    
        setupPagination(messages.length);
    }
    
    
    
    function setupPagination(totalMessages) {
        const totalPages = Math.ceil(totalMessages / messagesPerPage);
        const pagination = $('#pagination');
        pagination.empty();
    
        for (let i = 1; i <= totalPages; i++) {
            pagination.append(`
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#">${i}</a>
                </li>
            `);
        }
    
        $('.page-item a').on('click', function (e) {
            e.preventDefault();
            currentPage = parseInt($(this).text());
            displayMessages(filteredMessages);
        });
    }
    
    $('#filterButton').on('click', function () {
        const start_date = moment($('#start_date').val(), 'DD-MM-YYYY').format('YYYY-MM-DD');
        const end_date = moment($('#end_date').val(), 'DD-MM-YYYY').format('YYYY-MM-DD');
        const user_id = $('#user_id').val();
        const chat_id = $('#chat_id').val();
    
        let url = `/api/messages?start_date=${start_date || ''}&end_date=${end_date || ''}&user_id=${user_id || ''}&chat_id=${chat_id || ''}`;
    
        $('#loadingIcon').show();
        $.ajax({
            url,
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: function (data) {
                $('#loadingIcon').hide();
                $('#messagesContainer').show();
        
                // Проверяем, что 'data.messages' — массив
                if (Array.isArray(data.messages)) {
                    filteredMessages = data.messages; // Сохраняем массив сообщений
                    currentPage = 1; // Сбрасываем на первую страницу
                    displayMessages(filteredMessages); // Отображаем только текущую страницу
                } else {
                    alert('Ошибка: Ожидался массив сообщений.');
                }
            },
            error: function () {
                $('#loadingIcon').hide();
                alert('Ошибка при загрузке сообщений.');
            },
        });
        
    });
    
    
    $('#submitButton').on('click', function () {
        console.log(filteredMessages); // Убедитесь, что это массив и содержит все сообщения

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
            start_date: $('#start_date').val() || null,
            end_date: $('#end_date').val() || null,
            user_id: $('#user_id').val() || null,
            chat_id: $('#chat_id').val() || null,
        };
    
        $('#loadingIcon').show();
        $.ajax({
            url: '/analysis/create',
            type: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            contentType: 'application/json',
            data: JSON.stringify({ prompt_id, filters, messages: filteredMessages }),

            success: function (response) {
                $('#loadingIcon').hide();
                if (response.analysis_id && response.result_text) {
                    // Отображаем результат на текущей странице
                    $('#analysisResult').show();
                    $('#analysisContent').html(`
                        <p><strong>Анализ:</strong> ${response.result_text}</p>
                        <p><strong>ID анализа:</strong> ${response.analysis_id}</p>
                    `);
                    alert('Анализ успешно создан!');
                } else {
                    alert('Анализ создан, но результат пуст.');
                }
            },
            error: function () {
                $('#loadingIcon').hide();
                alert('Ошибка при создании анализа.');
            },
        });
    });
    
    
    function loadChats() {
        $.ajax({
            url: '/api/chats',
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: function (chats) {
                const chatSelect = $('#chat_id');
                chatSelect.empty();
                chatSelect.append('<option value="">-- Выберите чат --</option>');

                chats.forEach(chat => {
                    chatSelect.append(`<option value="${chat.chat_id}" data-default-prompt-id="${chat.default_prompt_id || ''}">${chat.chat_name}</option>`);
                });

                chatSelect.on('change', function () {
                    const selectedChat = $(this).find('option:selected');
                    const chatPromptId = selectedChat.data('default-prompt-id');

                    if (chatPromptId) {
                        console.log(`Выбран чат с дефолтным промптом: ${chatPromptId}`);
                        $('#prompt_name').val(chatPromptId);
                    } else {
                        console.log('У выбранного чата нет дефолтного промпта. Возвращаемся к основному.');
                        $('#prompt_name').val(defaultPromptId || '');
                    }
                });
            },
            error: function () {
                alert('Ошибка при загрузке чатов.');
            },
        });
    }


    function loadUsers() {
        $.ajax({
            url: '/api/users',
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: function (users) {
                const userSelect = $('#user_id');
                userSelect.empty();
                userSelect.append('<option value="">-- Выберите пользователя --</option>');
    
                users.forEach(user => {
                    userSelect.append(`<option value="${user.user_id}">${user.username || 'Без имени'}</option>`);
                });
    
                console.log('Список пользователей успешно загружен:', users);
            },
            error: function () {
                alert('Ошибка при загрузке пользователей.');
            },
        });
    }
    
});
