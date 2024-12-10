$(document).ready(function () {
    const token = localStorage.getItem('access_token');
    let filteredMessages = []; // Хранение всех сообщений после фильтрации

    let prompts = []; // Список всех промптов
    let defaultPromptId = null; // ID основного дефолтного промпта
    let currentPage = 1; // Текущая страница
    const pageSize = 10; // Количество сообщений на странице

    if (!token) {
        window.location.href = '/';
    } else {
        $.ajax({
            url: '/protected',
            type: 'GET',
            headers: {
                Authorization: `Bearer ${token}`,
            },
            success: function () {
                loadPrompts().then(() => {
                    checkAutomaticPrompt(); // Проверяем основной дефолтный промпт
                });
                loadChats();
            },
            error: function () {
                window.location.href = '/';
            },
        });
    }

    // Настройка диапазона дат
    $('#start_date').daterangepicker({
        singleDatePicker: true,
        autoApply: true,
        locale: { format: 'DD-MM-YYYY' },
    });

    $('#end_date').daterangepicker({
        singleDatePicker: true,
        autoApply: true,
        locale: { format: 'DD-MM-YYYY' },
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
            headers: { Authorization: `Bearer ${token}` },
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
                        $('#prompt_name').val(chatPromptId);
                    } else {
                        $('#prompt_name').val(defaultPromptId || '');
                    }
                });
            },
            error: function () {
                alert('Ошибка при загрузке чатов.');
            },
        });
    }


    window.downloadFile = function (s3Key) {
        $.ajax({
            url: `/api/download?s3_key=${encodeURIComponent(s3Key)}`,
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            success: function (response) {
                if (response.url) {
                    window.location.href = response.url;
                } else {
                    alert('Ошибка при генерации URL для скачивания.');
                }
            },
            error: function () {
                alert('Ошибка при скачивании файла.');
            },
        });
    };


    // Получение всех сообщений для анализа
    function fetchAllMessagesForAnalysis(filters) {
        return $.ajax({
            url: '/api/analyze',
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            data: filters,
            success: function (response) {
                filteredMessagesMessages = response.messages;
                console.log(`Всего сообщений для анализа: ${filteredMessages.length}`);
            },
            error: function () {
                alert('Ошибка при загрузке всех сообщений для анализа.');
            },
        });
    }

    // Получение сообщений для отображения с пагинацией
    function fetchPaginatedMessages(filters) {
        filters.page = currentPage;
        filters.page_size = pageSize;
        return $.ajax({
            url: '/api/messages',
            type: 'GET',
            headers: { Authorization: `Bearer ${token}` },
            data: filters,
            success: function (response) {
                paginatedMessages = response.messages;
                setupPagination(response.total);
                displayMessages();
            },
            error: function () {
                alert('Ошибка при загрузке сообщений для отображения.');
            },
        });
    }

    function setupPagination(totalMessages) {
        const totalPages = Math.ceil(totalMessages / pageSize);
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
            fetchPaginatedMessages(getFilters());
        });
    }

    function displayMessages() {
        const messagesTableBody = $('#messagesTable tbody');
        messagesTableBody.empty();

        paginatedMessages.forEach(msg => {
            const date = msg.timestamp ? moment(msg.timestamp).format('DD-MM-YYYY HH:mm:ss') : 'Не указано';
            const userId = msg.user_id || 'Не указано';
            const chatId = msg.chat_id || 'Не указано';
            const text = msg.text || 'Пустое сообщение';
            const s3Key = msg.s3_key || 'Не указано';

            messagesTableBody.append(`
                <tr>
                    <td>${date}</td>
                    <td>${userId}</td>
                    <td>${chatId}</td>
                    <td>${text}</td>
                    <td>${s3Key !== 'Не указано' ? `<button class="btn btn-primary btn-sm" onclick="downloadFile('${s3Key}')">Скачать</button>` : '—'}</td>
                </tr>
            `);
        });
    }

    function getFilters() {
        const start_date = moment($('#start_date').val(), 'DD-MM-YYYY').format('YYYY-MM-DD');
        const end_date = moment($('#end_date').val(), 'DD-MM-YYYY').format('YYYY-MM-DD');
        const user_id = $('#user_id').val();
        const chat_id = $('#chat_id').val();

        return {
            start_date,
            end_date,
            user_id,
            chat_id,
        };
    }

    $('#filterButton').on('click', function () {
        const filters = getFilters();

        fetchAllMessagesForAnalysis(filters).then(() => {
            currentPage = 1; // Сброс на первую страницу
            fetchPaginatedMessages(filters);
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

        const filters = getFilters();

        $('#loadingIcon').show();
        $.ajax({
            url: '/analysis/create',
            type: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            contentType: 'application/json',
            data: JSON.stringify({ prompt_id, filters, messages: filteredMessages}),
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
