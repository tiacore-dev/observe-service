$(document).ready(function () {
    const token = localStorage.getItem('access_token');
    let filteredMessages = []; // Хранение всех сообщений после фильтрации
    let currentPage = 1; // Текущая страница для отображения
    const messagesPerPage = 10; // Количество сообщений на страницу
    let prompts = []; // Список всех промптов
    let defaultPromptId = null; // ID основного дефолтного промпта

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

    function displayMessages(messages) {
        if (!Array.isArray(messages)) {
            console.error('Ошибка: Ожидается массив сообщений.');
            return;
        }

        const start = (currentPage - 1) * messagesPerPage;
        const end = start + messagesPerPage;
        const paginatedMessages = messages.slice(start, end);

        const messagesTableBody = $('#messagesTable tbody');
        messagesTableBody.empty(); // Очищаем таблицу перед добавлением новых сообщений

        paginatedMessages.forEach(msg => {
            const date = msg.timestamp ? moment(msg.timestamp).format('DD-MM-YYYY HH:mm:ss') : 'Не указано';
            const userId = msg.user_id || 'Не указано';
            const chatId = msg.chat_id || 'Не указано';
            const text = msg.text || 'Пустое сообщение';
            const s3Key = msg.s3_key || null;

            const downloadButton = s3Key
                ? `<button class="btn btn-sm btn-primary" onclick="downloadFile('${s3Key}')">Скачать</button>`
                : 'Нет файла';

            const row = `
                <tr>
                    <td>${date}</td>
                    <td>${userId}</td>
                    <td>${chatId}</td>
                    <td>${text}</td>
                    <td>${downloadButton}</td>
                </tr>
            `;
            messagesTableBody.append(row);
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

                if (Array.isArray(data.messages)) {
                    filteredMessages = data.messages;
                    currentPage = 1; // Сбрасываем на первую страницу
                    displayMessages(filteredMessages);
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
});
