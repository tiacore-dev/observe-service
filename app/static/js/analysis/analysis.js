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
                loadChats();
            },
            error: function () {
                window.location.href = '/';
            }
        });
    }

    // Настройка диапазона дат
    $('#start_date').daterangepicker({
        singleDatePicker: true,
        //locale: { format: 'YYYY-MM-DD' },
        locale: { format: 'DD-MM-YYYY' },
    });
    $('#end_date').daterangepicker({
        singleDatePicker: true,
        //locale: { format: 'YYYY-MM-DD' },
        locale: { format: 'DD-MM-YYYY' },
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

    let currentPage = 1;
    const messagesPerPage = 10;
    
    function displayMessages(messages) {
        const start = (currentPage - 1) * messagesPerPage;
        const end = start + messagesPerPage;
        const paginatedMessages = messages.slice(start, end);
    
        const messagesList = $('#messagesList');
        messagesList.empty();
        paginatedMessages.forEach(msg => {
            messagesList.append(`<div class="message-item">${msg.content}</div>`);
        });
    
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
        const start_date = $('#start_date').val();
        const end_date = $('#end_date').val();
        const user_id = $('#user_id').val();
        const chat_id = $('#chat_id').val();
    
        let url = `/api/messages?start_date=${start_date || ''}&end_date=${end_date || ''}&user_id=${user_id || ''}&chat_id=${chat_id || ''}`;
    
        $('#loadingIcon').show();
        $.ajax({
            url,
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: (data) => {
                $('#loadingIcon').hide();
                $('#messagesContainer').show();
    
                // Сохраняем все найденные сообщения в переменную
                filteredMessages = data;
                currentPage = 1; // Сбрасываем на первую страницу
                displayMessages(filteredMessages); // Отображаем только текущую страницу
            },
            error: () => {
                $('#loadingIcon').hide();
                alert('Ошибка при загрузке сообщений.');
            },
        });
    });
    
    
    $('#submitButton').on('click', function () {
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
                        <p><strong>Сообщение:</strong> ${response.result_text}</p>
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
                chatSelect.empty(); // Очищаем выпадающий список
                chatSelect.append('<option value="">-- Выберите чат --</option>'); // Опция по умолчанию
    
                chats.forEach(chat => {
                    chatSelect.append(`<option value="${chat.chat_id}">${chat.chat_name}</option>`);
                });
            },
            error: function () {
                alert('Ошибка при загрузке чатов.');
            },
        });
    }
});
