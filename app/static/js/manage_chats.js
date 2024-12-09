$(document).ready(function () {
    $('.save-prompt-btn').on('click', function () {
        const chatId = $(this).data('chat-id');
        const promptId = $(`.prompt-select[data-chat-id="${chatId}"]`).val();

        if (!promptId) {
            alert('Пожалуйста, выберите промпт.');
            return;
        }

        $.ajax({
            url: '/update_chat_prompt',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ chat_id: chatId, prompt_id: promptId }),
            success: function (response) {
                alert('Дефолтный промпт успешно обновлён!');
            },
            error: function (xhr) {
                alert(xhr.responseJSON.error || 'Ошибка при обновлении промпта.');
            }
        });
    });
});
