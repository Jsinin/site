// === ЗАГРУЗКА И ОТОБРАЖЕНИЕ ДАННЫХ ===
document.addEventListener('DOMContentLoaded', function() {
    // Получаем результаты из localStorage
    const savedResults = localStorage.getItem('turbineResults');
    
    if (!savedResults) {
        alert('Нет данных для отображения. Пожалуйста, выполните расчет на главной странице.');
        window.location.href = 'index.html';
        return;
    }
    
    const results = JSON.parse(savedResults);
    console.log('Загружены данные для h-s диаграммы:', results);
    
    // Строим диаграмму
    buildHsDiagram(results);
    
    // Заполняем таблицу
    fillPointsTable(results);
    
    // Обновляем заголовок
    updateTitle(results);
});

// === ПОСТРОЕНИЕ h-s ДИАГРАММЫ ===
function buildHsDiagram(results) {
    const points = results.points || [];
    
    // Извлекаем данные для графика
    const s_values = points.map(p => p.s); // энтропия
    const h_values = points.map(p => p.h); // энтальпия
    const labels = points.map(p => p.name);
    
    // Создаем график Plotly
    const trace = {
        x: s_values,
        y: h_values,
        mode: 'lines+markers+text',
        type: 'scatter',
        name: 'Процесс расширения',
        line: {
            color: '#764ba2',
            width: 3,
            shape: 'spline'
        },
        marker: {
            size: 10,
            color: '#667eea',
            symbol: 'circle',
            line: {
                color: '#764ba2',
                width: 2
            }
        },
        text: labels.map((label, i) => `${i + 1}`),
        textposition: 'top center',
        textfont: {
            size: 11,
            color: '#333'
        },
        hovertemplate: 
            '<b>%{text}</b><br>' +
            'Точка: ' + labels.join('<br>') + '<br>' +
            'Энтальпия: %{y:.1f} кДж/кг<br>' +
            'Энтропия: %{x:.4f} кДж/(кг·К)<br>' +
            '<extra></extra>'
    };
    
    // Добавляем подписи для каждой точки
    const annotations = points.map((point, i) => ({
        x: point.s,
        y: point.h,
        xref: 'x',
        yref: 'y',
        text: `${i + 1}. ${point.name}`,
        showarrow: true,
        arrowhead: 2,
        arrowsize: 1,
        arrowwidth: 1,
        arrowcolor: '#764ba2',
        ax: 20,
        ay: -30,
        bordercolor: '#764ba2',
        borderwidth: 1,
        borderpad: 4,
        bgcolor: '#f8f5ff',
        opacity: 0.9,
        font: {
            size: 10,
            color: '#333'
        }
    }));
    
    const layout = {
        title: {
            text: `h-s Диаграмма (${results.mode === 'cond' ? 'Конденсационный' : 'Теплофикационный'} режим)`,
            font: {
                size: 20,
                color: '#764ba2'
            }
        },
        xaxis: {
            title: {
                text: 'Энтропия s, кДж/(кг·К)',
                font: {
                    size: 16,
                    color: '#555'
                }
            },
            gridcolor: '#e0d4fc',
            zerolinecolor: '#764ba2',
            zerolinewidth: 2
        },
        yaxis: {
            title: {
                text: 'Энтальпия h, кДж/кг',
                font: {
                    size: 16,
                    color: '#555'
                }
            },
            gridcolor: '#e0d4fc',
            zerolinecolor: '#764ba2',
            zerolinewidth: 2
        },
        plot_bgcolor: '#faf8ff',
        paper_bgcolor: '#faf8ff',
        hovermode: 'closest',
        showlegend: true,
        legend: {
            x: 0.02,
            y: 0.98,
            bgcolor: 'rgba(255, 255, 255, 0.8)',
            bordercolor: '#764ba2',
            borderwidth: 1
        },
        annotations: annotations,
        margin: {
            l: 80,
            r: 80,
            t: 80,
            b: 80
        }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToAdd: ['drawline', 'eraseshape'],
        displaylogo: false
    };
    
    // Рисуем график
    Plotly.newPlot('hsDiagram', [trace], layout, config);
    
    // Добавляем информацию о режиме
    addInfoPanel(results);
}

// === ДОБАВЛЕНИЕ ИНФОРМАЦИОННОЙ ПАНЕЛИ ===
function addInfoPanel(results) {
    const infoDiv = document.createElement('div');
    infoDiv.className = 'diagram-info';
    infoDiv.innerHTML = `
        <div class="info-card">
            <h3>📊 Параметры расчета</h3>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Режим:</span>
                    <span class="info-value">${results.mode === 'cond' ? 'Конденсационный' : 'Теплофикационный'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Мощность:</span>
                    <span class="info-value">${results.total_power.toFixed(2)} МВт</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Расход пара:</span>
                    <span class="info-value">${results.D0_th.toFixed(1)} т/ч</span>
                </div>
                <div class="info-item">
                    <span class="info-label">КПД:</span>
                    <span class="info-value">${results.efficiency.toFixed(2)}%</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Точек на диаграмме:</span>
                    <span class="info-value">${results.points.length}</span>
                </div>
            </div>
        </div>
    `;
    
    // Вставляем перед графиком
    const chartContainer = document.querySelector('.chart-container');
    chartContainer.insertBefore(infoDiv, chartContainer.firstChild);
}

// === ЗАПОЛНЕНИЕ ТАБЛИЦЫ ===
function fillPointsTable(results) {
    const tbody = document.getElementById('pointsTableBody');
    const points = results.points || [];
    
    tbody.innerHTML = '';
    
    points.forEach((point, index) => {
        const row = document.createElement('tr');
        
        // Определяем класс для строки (отборы выделяем цветом)
        const rowClass = point.is_extraction ? 'extraction-row' : '';
        row.className = rowClass;
        
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${point.name}</strong></td>
            <td>${point.P.toFixed(4)}</td>
            <td>${point.T > 0 ? point.T.toFixed(1) : 'Н/Д'}</td>
            <td>${point.h.toFixed(2)}</td>
            <td>${point.s.toFixed(4)}</td>
            <td>${point.G.toFixed(2)}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// === ОБНОВЛЕНИЕ ЗАГОЛОВКА ===
function updateTitle(results) {
    const title = document.querySelector('.scheme-title');
    const modeText = results.mode === 'cond' ? 'Конденсационный' : 'Теплофикационный';
    title.textContent = `h-s Диаграмма - ${modeText} режим`;
}

// === ЭКСПОРТ ГРАФИКА ===
function exportDiagram() {
    Plotly.downloadImage('hsDiagram', {
        format: 'png',
        width: 1200,
        height: 800,
        filename: 'hs-diagram-turbine'
    });
}

// Делаем функцию доступной глобально
window.exportDiagram = exportDiagram;