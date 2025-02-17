$(document).ready(function () {
    const token = localStorage.getItem('access_token');
    const pathParts = window.location.pathname.split('/');
    const analysisId = pathParts[pathParts.indexOf('analysis') + 1]; 

    console.log(`Extracted analysisId: ${analysisId}`);

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
                loadAnalysisDetails(analysisId);
            },
            error: function () {
                window.location.href = '/';
            }
        });
    }

    function calculateCost(tokens, ratePer1000) {
        return ((tokens / 1000) * ratePer1000).toFixed(2);
    }

    function formatDate(timestamp) {
        if (!timestamp) return "Не указано";
    
        const date = new Date(timestamp);
        return date.toLocaleString("ru-RU", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        }).replace(",", ""); // Убираем запятую между датой и временем
    }
    

    function loadAnalysisDetails(analysisId) {
        $('#loadingIndicator').show();
        $.ajax({
            url: `/analysis/${analysisId}`,
            type: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            success: function (response) {
                const rateInput = 0.03; // Цена за 1000 токенов на ввод (в $)
                const rateOutput = 0.06; // Цена за 1000 токенов на вывод (в $)

                $('#promptName').text(response.prompt_name);
                $('#filters').text(response.filters || 'Не указаны');
                $('#analysisText').text(response.result_text);
                $('#tokensInput').text(response.tokens_input || 'Неизвестно');
                $('#costInput').text(
                    calculateCost(response.tokens_input || 0, rateInput)
                );
                $('#tokensOutput').text(response.tokens_output || 'Неизвестно');
                $('#costOutput').text(
                    calculateCost(response.tokens_output || 0, rateOutput)
                );
                $('#timestamp').text(formatDate(response.timestamp));
                $('#loadingIndicator').hide();
            },
            error: function () {
                alert('Ошибка при загрузке данных анализа.');
                $('#loadingIndicator').hide();
            }
        });
    }

    $('#backButton').on('click', function () {
        window.location.href = '/analysis_result';
    });
});
