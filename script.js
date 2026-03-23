let currentTurbine = 'cond';

// === ФУНКЦИЯ ОТПРАВКИ ДАННЫХ НА API ===
async function sendToAPI(params) {
    try {
        const response = await fetch('https://turbine-4sh4.onrender.com', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Сохраняем результаты для использования на странице схемы
            localStorage.setItem('turbineResults', JSON.stringify(result.data));
            return result.data;
        } else {
            console.error('Ошибка расчета:', result.error);
            alert('Ошибка при расчете: ' + result.error);
            return null;
        }
    } catch (error) {
        console.error('Ошибка подключения к API:', error);
        alert('Не удалось подключиться к серверу расчета. Убедитесь, что API запущен (шаг 1).');
        return null;
    }
}

// === ФУНКЦИЯ ОБНОВЛЕНИЯ СХЕМЫ С РЕЗУЛЬТАТАМИ ===
function updateSchemeWithResults(results) {
    if (!results) return;
    
    console.log('Обновление схемы с результатами:', results);
    
    // Обновляем заголовок
    const schemeTitle = document.querySelector('.scheme-title');
    if (schemeTitle) {
        const modeText = results.mode === 'cond' ? 'Конденсационный' : 'Теплофикационный';
        schemeTitle.textContent = `Схема турбины - ${modeText} режим`;
    }
    
    // Получаем все точки для удобного доступа
    const pointsMap = {};
    results.points.forEach(point => {
        const name = point.name.toLowerCase();
        pointsMap[name] = point;
    });
    
    // === ОБНОВЛЕНИЕ КАЖДОГО ЭЛЕМЕНТА ===
    
    // 1. Генератор
    const generator = document.querySelector('[data-id="generator"]');
    if (generator && results.total_power) {
        const desc = `⚡ ГЕНЕРАТОР\n\n` +
                     `Электрическая мощность: ${results.total_power.toFixed(2)} МВт\n` +
                     `Мощность брутто: ${results.gross_power.toFixed(2)} МВт\n` +
                     `Напряжение: 20 кВ\n` +
                     `КПД генератора: 96%\n` +
                     `Расход пара: ${results.D0_th.toFixed(1)} т/ч\n` +
                     `Удельный расход пара: ${results.specific_steam_consumption.toFixed(3)} кг/кВт·ч`;
        generator.setAttribute('data-desc', desc);
    }
    
    // 2. Турбина ЦВД (высокого давления)
    const turbineHP = document.querySelector('[data-id="turbine-hp"]');
    if (turbineHP) {
        const point = pointsMap['отбор 1'] || pointsMap['свежий пар'];
        if (point) {
            const desc = `🔧 ТУРБИНА ЦВД\n\n` +
                         `Давление на входе: ${results.points[0]?.P.toFixed(3) || '12.75'} МПа\n` +
                         `Температура на входе: ${results.points[0]?.T.toFixed(1) || '540'}°C\n` +
                         `Давление на выходе: ${point.P.toFixed(3)} МПа\n` +
                         `Температура на выходе: ${point.T.toFixed(1)}°C\n` +
                         `Энтальпия: ${point.h.toFixed(1)} кДж/кг\n` +
                         `Расход пара: ${point.G.toFixed(1)} кг/с`;
            turbineHP.setAttribute('data-desc', desc);
        }
    }
    
    // 3. Турбина ЦСД (среднего давления)
    const turbineIP = document.querySelector('[data-id="turbine-ip"]');
    if (turbineIP) {
        const point = pointsMap['отбор 2'] || pointsMap['отбор 3'];
        if (point) {
            const desc = `🔧 ТУРБИНА ЦСД\n\n` +
                         `Давление: ${point.P.toFixed(3)} МПа\n` +
                         `Температура: ${point.T > 0 ? point.T.toFixed(1) : 'Н/Д'}°C\n` +
                         `Энтальпия: ${point.h.toFixed(1)} кДж/кг\n` +
                         `Расход пара: ${point.G.toFixed(1)} кг/с\n` +
                         `Энтропия: ${point.s.toFixed(4)} кДж/(кг·К)`;
            turbineIP.setAttribute('data-desc', desc);
        }
    }
    
    // 4. Турбина ЦНД (низкого давления)
    const turbineLP = document.querySelector('[data-id="turbine-lp"]');
    if (turbineLP) {
        const condPoint = pointsMap['конденсатор'];
        if (condPoint) {
            const desc = `🔧 ТУРБИНА ЦНД\n\n` +
                         `Давление на выходе: ${condPoint.P.toFixed(4)} МПа\n` +
                         `Температура: ${condPoint.T.toFixed(1)}°C\n` +
                         `Расход пара: ${condPoint.G.toFixed(1)} кг/с\n` +
                         `Степень сухости: ${(condPoint.x || 0.9).toFixed(3)}\n` +
                         `Энтальпия: ${condPoint.h.toFixed(1)} кДж/кг`;
            turbineLP.setAttribute('data-desc', desc);
        }
    }
    
    // 5. Конденсатор 1
    const condenser1 = document.querySelector('[data-id="condenser-1"]');
    if (condenser1) {
        const condPoint = pointsMap['конденсатор'];
        if (condPoint) {
            const desc = `❄️ КОНДЕНСАТОР 1\n\n` +
                         `Давление: ${condPoint.P.toFixed(4)} МПа\n` +
                         `Температура конденсации: ${condPoint.T.toFixed(1)}°C\n` +
                         `Расход пара: ${condPoint.G.toFixed(1)} кг/с\n` +
                         `Энтальпия: ${condPoint.h.toFixed(1)} кДж/кг\n` +
                         `Степень сухости: ${(condPoint.x || 0).toFixed(3)}`;
            condenser1.setAttribute('data-desc', desc);
        }
    }
    
    // 6. Конденсатор 2
    const condenser2 = document.querySelector('[data-id="condenser-2"]');
    if (condenser2) {
        const condPoint = pointsMap['конденсатор'];
        if (condPoint) {
            const desc = `❄️ КОНДЕНСАТОР 2\n\n` +
                         `Давление: ${condPoint.P.toFixed(4)} МПа\n` +
                         `Температура: ${condPoint.T.toFixed(1)}°C\n` +
                         `Расход охлаждающей воды: ~15000 м³/ч\n` +
                         `Тепловая нагрузка: ${(condPoint.G * 2.5 / 1000).toFixed(2)} МВт`;
            condenser2.setAttribute('data-desc', desc);
        }
    }
    
    // 7. Деаэратор
    const deaerator = document.querySelector('[data-id="deaerator"]');
    if (deaerator) {
        const deaerPoint = pointsMap['отбор 4'];
        if (deaerPoint) {
            const desc = `💧 ДЕАЭРАТОР\n\n` +
                         `Давление: ${deaerPoint.P.toFixed(3)} МПа\n` +
                         `Температура: ${deaerPoint.T.toFixed(1)}°C\n` +
                         `Энтальпия: ${deaerPoint.h.toFixed(1)} кДж/кг\n` +
                         `Расход пара на деаэрацию: ${deaerPoint.G.toFixed(1)} кг/с\n` +
                         `Емкость: 100 м³`;
            deaerator.setAttribute('data-desc', desc);
        }
    }
    
    // 8-10. ПВД (подогреватели высокого давления)
    const pvd7 = document.querySelector('[data-id="hph-1"]');
    if (pvd7) {
        const pvdPoint = pointsMap['отбор 1'] || pointsMap['регенеративный отбор 1'];
        if (pvdPoint) {
            const desc = `🔥 ПВД-7\n\n` +
                         `Давление отбора: ${pvdPoint.P.toFixed(2)} МПа\n` +
                         `Температура: ${pvdPoint.T.toFixed(1)}°C\n` +
                         `Расход пара: ${pvdPoint.G.toFixed(1)} кг/с\n` +
                         `Энтальпия: ${pvdPoint.h.toFixed(1)} кДж/кг\n` +
                         `Поверхность нагрева: ~500 м²`;
            pvd7.setAttribute('data-desc', desc);
        }
    }
    
    const pvd6 = document.querySelector('[data-id="hph-2"]');
    if (pvd6) {
        const pvdPoint = pointsMap['отбор 2'] || pointsMap['регенеративный отбор 2'];
        if (pvdPoint) {
            const desc = `🔥 ПВД-6\n\n` +
                         `Давление отбора: ${pvdPoint.P.toFixed(2)} МПа\n` +
                         `Температура: ${pvdPoint.T.toFixed(1)}°C\n` +
                         `Расход пара: ${pvdPoint.G.toFixed(1)} кг/с\n` +
                         `Энтальпия: ${pvdPoint.h.toFixed(1)} кДж/кг`;
            pvd6.setAttribute('data-desc', desc);
        }
    }
    
    const pvd5 = document.querySelector('[data-id="hph-3"]');
    if (pvd5) {
        const pvdPoint = pointsMap['отбор 3'] || pointsMap['регенеративный отбор 3'];
        if (pvdPoint) {
            const desc = `🔥 ПВД-5\n\n` +
                         `Давление отбора: ${pvdPoint.P.toFixed(2)} МПа\n` +
                         `Температура: ${pvdPoint.T.toFixed(1)}°C\n` +
                         `Расход пара: ${pvdPoint.G.toFixed(1)} кг/с\n` +
                         `Энтальпия: ${pvdPoint.h.toFixed(1)} кДж/кг`;
            pvd5.setAttribute('data-desc', desc);
        }
    }
    
    // 11-14. ПНД (подогреватели низкого давления)
    const pnd4 = document.querySelector('[data-id="lph-1"]');
    if (pnd4) {
        const desc = `🔥 ПНД-4\n\n` +
                     `Давление: 0.15 МПа\n` +
                     `Температура: ~110°C\n` +
                     `Поверхность нагрева: ~300 м²\n` +
                     `Подогрев питательной воды`;
        pnd4.setAttribute('data-desc', desc);
    }
    
    const pnd3 = document.querySelector('[data-id="lph-2"]');
    if (pnd3) {
        const desc = `🔥 ПНД-3\n\n` +
                     `Давление: 0.08 МПа\n` +
                     `Температура: ~90°C\n` +
                     `Поверхность нагрева: ~280 м²`;
        pnd3.setAttribute('data-desc', desc);
    }
    
    const pnd2 = document.querySelector('[data-id="lph-3"]');
    if (pnd2) {
        const desc = `🔥 ПНД-2\n\n` +
                     `Давление: 0.04 МПа\n` +
                     `Температура: ~75°C\n` +
                     `Поверхность нагрева: ~250 м²`;
        pnd2.setAttribute('data-desc', desc);
    }
    
    const pnd1 = document.querySelector('[data-id="lph-4"]');
    if (pnd1) {
        const desc = `🔥 ПНД-1\n\n` +
                     `Давление: 0.02 МПа\n` +
                     `Температура: ~60°C\n` +
                     `Поверхность нагрева: ~220 м²`;
        pnd1.setAttribute('data-desc', desc);
    }
    
    console.log('✅ Схема обновлена расчетными данными');
}

// === ПЕРЕКЛЮЧЕНИЕ ТУРБИНЫ ===
function swapTurbine(direction) {
    const condImage = document.getElementById('condImage');
    const heatImage = document.getElementById('heatImage');
    const condParams = document.getElementById('condParams');
    const heatParams = document.getElementById('heatParams');
    const turbineLabel = document.getElementById('turbineLabel');
    
    if (!condImage || !heatImage) return;
    
    const exitClass = direction === 'left' ? 'exit-left' : 'exit-right';
    
    if (currentTurbine === 'cond') {
        condImage.classList.remove('active');
        condImage.classList.add(exitClass);
        
        setTimeout(() => {
            heatImage.classList.remove('exit-left', 'exit-right');
            heatImage.classList.add('active');
        }, 100);
        
        condParams.classList.remove('active');
        setTimeout(() => {
            heatParams.classList.add('active');
        }, 300);
        
        turbineLabel.textContent = 'Теплофикационный';
        currentTurbine = 'heat';
        
    } else {
        heatImage.classList.remove('active');
        heatImage.classList.add(exitClass);
        
        setTimeout(() => {
            condImage.classList.remove('exit-left', 'exit-right');
            condImage.classList.add('active');
        }, 100);
        
        heatParams.classList.remove('active');
        setTimeout(() => {
            condParams.classList.add('active');
        }, 300);
        
        turbineLabel.textContent = 'Конденсационный';
        currentTurbine = 'cond';
    }
    
    setTimeout(() => {
        if (condImage) condImage.classList.remove('exit-left', 'exit-right');
        if (heatImage) heatImage.classList.remove('exit-left', 'exit-right');
    }, 700);
}

// === ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ ===
document.addEventListener('DOMContentLoaded', function() {
    // === Обработка tooltips на схеме ===
    const schemeElements = document.querySelectorAll('.scheme-element.interactive');
    const tooltip = document.getElementById('tooltip');
    const tooltipTitle = document.getElementById('tooltipTitle');
    const tooltipDesc = document.getElementById('tooltipDesc');
    
    if (schemeElements.length > 0 && tooltip) {
        schemeElements.forEach(element => {
            element.addEventListener('mouseenter', function(e) {
                const name = this.getAttribute('data-name');
                const desc = this.getAttribute('data-desc');
                
                if (tooltipTitle && tooltipDesc) {
                    tooltipTitle.textContent = name;
                    tooltipDesc.innerHTML = desc.replace(/&#10;/g, '<br>');
                }
                
                tooltip.classList.add('show');
                positionTooltip(e);
            });
            
            element.addEventListener('mousemove', function(e) {
                positionTooltip(e);
            });
            
            element.addEventListener('mouseleave', function() {
                tooltip.classList.remove('show');
            });
        });
    }
    
    // === Обработка кнопки "Рассчитать" ===
    const calcButton = document.getElementById('calcButton');
    if (calcButton) {
        calcButton.addEventListener('click', async function(e) {
            e.preventDefault(); // Отменяем стандартный переход
            
            const condPower = document.getElementById('condPower');
            const heatLoad = document.getElementById('heatLoad');
            const heatTemp = document.getElementById('heatTemp');
            
            // Проверка заполнения полей
            if (currentTurbine === 'cond' && (!condPower || !condPower.value)) {
                alert('Пожалуйста, введите мощность турбины');
                return;
            }
            
            if (currentTurbine === 'heat' && (!heatLoad || !heatLoad.value)) {
                alert('Пожалуйста, введите тепловую нагрузку');
                return;
            }
            
            const params = {
                turbineType: currentTurbine,
                condPower: condPower ? parseFloat(condPower.value) : 0,
                heatLoad: heatLoad ? parseFloat(heatLoad.value) : 0,
                heatTemp: heatTemp ? parseFloat(heatTemp.value) : 0,
                tempSupply: document.getElementById('tempSupply') ? parseFloat(document.getElementById('tempSupply').value) : 150,
                tempReturn: document.getElementById('tempReturn') ? parseFloat(document.getElementById('tempReturn').value) : 70
            };
            
            console.log('Отправка параметров на API:', params);
            
            // Показываем индикатор загрузки
            const originalText = calcButton.innerHTML;
            calcButton.innerHTML = '⏳ Расчет...';
            calcButton.style.pointerEvents = 'none';
            calcButton.style.opacity = '0.7';
            
            // Отправляем на API
            const results = await sendToAPI(params);
            
            // Восстанавливаем кнопку
            calcButton.innerHTML = originalText;
            calcButton.style.pointerEvents = 'auto';
            calcButton.style.opacity = '1';
            
            if (results) {
                console.log('Получены результаты:', results);
                // Переходим на страницу схемы
                window.location.href = 'scheme.html';
            }
        });
    }
    
    // === Обновление схемы при загрузке (если есть результаты) ===
    const savedResults = localStorage.getItem('turbineResults');
    if (savedResults) {
        const results = JSON.parse(savedResults);
        console.log('Загружены сохраненные результаты:', results);
        updateSchemeWithResults(results);
    }
});

// === ПОЗИЦИОНИРОВАНИЕ TOOLTIP ===
function positionTooltip(e) {
    const tooltip = document.getElementById('tooltip');
    if (!tooltip) return;
    
    const xOffset = 20;
    const yOffset = 20;
    
    let left = e.clientX + xOffset;
    let top = e.clientY + yOffset;
    
    const rect = tooltip.getBoundingClientRect();
    
    if (left + rect.width > window.innerWidth) {
        left = e.clientX - rect.width - xOffset;
    }
    
    if (top + rect.height > window.innerHeight) {
        top = e.clientY - rect.height - yOffset;
    }
    
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
}