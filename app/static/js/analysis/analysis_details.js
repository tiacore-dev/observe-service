$(document).ready(function () {
    const token = localStorage.getItem('access_token');
    // Правильное извлечение analysisId из URL
    const pathParts = window.location.pathname.split('/');
    const analysisId = pathParts[pathParts.indexOf('analysis') + 1]; 
    // Логирование для отладки
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



    function loadAnalysisDetails(analysisId) {
        $('#loadingIndicator').show();
        $.ajax({
            url: `/analysis/${analysisId}`,
            type: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            success: function (response) {
                $('#promptName').text(response.prompt_name);
                $('#filters').text(response.filters || 'Не указаны');
                $('#analysisText').text(response.result_text);
                $('#analysisTokens').text(response.tokens || 'Неизвестно');
                $('#timestamp').text(new Date(response.timestamp).toLocaleString());
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
