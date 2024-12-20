$(document).ready(function () {
    const token = localStorage.getItem('access_token');
    let offset = 0;
    const limit = 10;

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
                loadAnalyses();
            },
            error: function () {
                window.location.href = '/';
            }
        });
    }

    function loadAnalyses() {
        $('#loadingIndicator').show();
        $.ajax({
            url: `/analysis/all?offset=${offset}&limit=${limit}`,
            type: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            success: function (response) {
                $('#loadingIndicator').hide();
                const tableBody = $('#analysisTable tbody');
                tableBody.empty();
    
                if (response.analyses.length === 0) {
                    tableBody.append('<tr><td colspan="4">Нет доступных анализов.</td></tr>');
                    return;
                }
    
                response.analyses.forEach(function (analysis, index) {
                    const rowNumber = offset + index + 1;
                    const trimmedFilters = analysis.filters ? JSON.stringify(analysis.filters) : 'Не указаны';
                
                    const row = `
                        <tr class="clickable-row" data-analysis-id="${analysis.analysis_id}">
                            <td>${rowNumber}</td>
                            <td>${analysis.prompt_name || 'Не указано'}</td>
                            <td>${trimmedFilters}</td>
                            <td>${new Date(analysis.timestamp).toLocaleString("ru-RU", { timeZone: "Asia/Novosibirsk" })}</td>
                        </tr>`;
                    tableBody.append(row);
                });
    
                $('.clickable-row').off('click').on('click', function () {
                    const analysisId = $(this).attr('data-analysis-id'); // Используем .attr() вместо .data()
                    if (analysisId) {
                        window.location.href = `/analysis/${analysisId}/view`;
                    } else {
                        console.error('Не удалось получить analysis_id из строки таблицы.');
                        alert('Ошибка: ID анализа не найден.');
                    }
                });
            },
            error: function () {
                $('#loadingIndicator').hide();
                alert('Ошибка при загрузке анализов.');
            }
        });
    }
    
});
