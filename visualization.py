"""
Модуль визуализации
Построение графиков и диаграмм
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from thermodynamics import SteamProperties

def plot_hs_diagram(points):
    """
    Построение процесса расширения в h-s координатах
    
    Параметры:
    points (list): Список точек процесса
    
    Возвращает:
    plotly.graph_objects.Figure: Фигура с диаграммой
    """
    fig = go.Figure()
    
    # Извлекаем координаты точек
    h_vals = [p['h'] for p in points if not p.get('is_extraction', False)]
    s_vals = [p['s'] for p in points if not p.get('is_extraction', False)]
    
    # Рисуем процесс расширения
    fig.add_trace(go.Scatter(
        x=s_vals,
        y=h_vals,
        mode='lines+markers',
        name='Процесс расширения',
        line=dict(color='red', width=3),
        marker=dict(size=10, color='red', symbol='circle')
    ))
    
    # Аннотации для каждой точки
    for i, p in enumerate(points):
        if not p.get('is_extraction', False):
            # Формируем текст аннотации
            text = f"{p['name']}<br>P={p['P']:.3f} МПа"
            if p['T'] > 0:
                text += f"<br>T={p['T']:.1f}°C"
            text += f"<br>h={p['h']:.1f} кДж/кг"
            
            fig.add_annotation(
                x=p['s'],
                y=p['h'],
                text=text,
                showarrow=True,
                arrowhead=2,
                ax=20,
                ay=(-1)**i * 30,
                font=dict(size=10)
            )
    
    # Настройка внешнего вида
    fig.update_layout(
        title='h-s Диаграмма процесса расширения',
        xaxis_title='Энтропия s (кДж/(кг·К))',
        yaxis_title='Энтальпия h (кДж/кг)',
        template='plotly_white',
        hovermode='closest',
        width=600,
        height=500
    )
    
    return fig

def plot_heat_load_chart(results):
    """
    Построение столбчатой диаграммы мощностей
    
    Параметры:
    results (dict): Результаты расчета
    
    Возвращает:
    plotly.graph_objects.Figure: Фигура с диаграммой
    """
    fig = go.Figure()
    
    # Данные для диаграммы
    categories = ['Электрическая мощность']
    values = [results['total_power']]
    colors = ['#1f77b4']
    
    if results.get('Q_network', 0) > 0:
        categories.append('Тепловая нагрузка')
        values.append(results['Q_network'])
        colors.append('#ff7f0e')
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        text=[f'{v:.1f} МВт' for v in values],
        textposition='auto',
        marker_color=colors,
        name='Мощность'
    ))
    
    fig.update_layout(
        title='Баланс мощностей',
        yaxis_title='Мощность (МВт)',
        template='plotly_white',
        showlegend=False,
        width=500,
        height=400
    )
    
    return fig

def plot_performance_curves(model, power_range=(50, 120)):
    """
    Построение характеристических кривых турбины
    
    Параметры:
    model: Модель турбины
    power_range (tuple): Диапазон мощностей (мин, макс)
    
    Возвращает:
    plotly.graph_objects.Figure: Фигура с кривыми
    """
    powers = np.linspace(power_range[0], power_range[1], 10)
    steam_flows = []
    efficiencies = []
    
    for power in powers:
        res = model.calculate_condensing_mode(power)
        steam_flows.append(res['D0'] * 3.6)  # т/ч
        efficiencies.append(res['efficiency'])
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Расход пара
    fig.add_trace(
        go.Scatter(x=powers, y=steam_flows, name='Расход пара', line=dict(color='blue', width=2)),
        secondary_y=False
    )
    
    # КПД
    fig.add_trace(
        go.Scatter(x=powers, y=efficiencies, name='КПД брутто', line=dict(color='red', width=2)),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text='Электрическая мощность (МВт)')
    fig.update_yaxes(title_text='Расход пара (т/ч)', secondary_y=False)
    fig.update_yaxes(title_text='КПД (%)', secondary_y=True)
    fig.update_layout(
        title='Характеристики турбины в конденсационном режиме',
        template='plotly_white',
        hovermode='x',
        width=700,
        height=450
    )
    
    return fig

def plot_extraction_characteristics():
    """
    Построение характеристик отборов (теплофикационный режим)
    
    Возвращает:
    plotly.graph_objects.Figure: Фигура с характеристиками
    """
    # Данные для графика (усредненные значения)
    # Q_thermal, P_el для разных режимов
    data = {
        'Q_thermal': [0, 20, 40, 60, 80, 100, 120],
        'P_el_max': [120, 115, 110, 100, 85, 70, 50],
        'P_el_min': [30, 35, 40, 45, 50, 55, 60]
    }
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['Q_thermal'],
        y=data['P_el_max'],
        mode='lines+markers',
        name='Максимальная мощность',
        line=dict(color='green', width=2),
        fill=None
    ))
    
    fig.add_trace(go.Scatter(
        x=data['Q_thermal'],
        y=data['P_el_min'],
        mode='lines+markers',
        name='Минимальная мощность',
        line=dict(color='orange', width=2),
        fill='tonexty',
        fillcolor='rgba(128, 128, 128, 0.2)'
    ))
    
    fig.update_layout(
        title='Режимная диаграмма турбины (Q-диаграмма)',
        xaxis_title='Тепловая нагрузка отборов (Гкал/ч)',
        yaxis_title='Электрическая мощность (МВт)',
        template='plotly_white',
        width=700,
        height=500
    )
    
    return fig

def plot_steam_flow_characteristics():
    """
    Построение расходной характеристики турбины
    
    Возвращает:
    plotly.graph_objects.Figure: Фигура с графиком
    """
    # Примерные данные для расходной характеристики
    power = np.linspace(30, 120, 10)
    steam_flow = 40 + 0.75 * power  # Упрощенная линейная зависимость
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=power,
        y=steam_flow,
        mode='lines+markers',
        name='Расход пара',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Расходная характеристика турбины',
        xaxis_title='Электрическая мощность (МВт)',
        yaxis_title='Расход пара (т/ч)',
        template='plotly_white',
        width=600,
        height=400
    )
    
    return fig


def plot_efficiency_curve():
    """
    Построение кривой КПД
    
    Возвращает:
    plotly.graph_objects.Figure: Фигура с графиком
    """
    # Примерные данные для кривой КПД
    power = np.linspace(30, 120, 10)
    efficiency = 35 + 10 * (1 - np.exp(-power/80))  # Упрощенная зависимость
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=power,
        y=efficiency,
        mode='lines+markers',
        name='КПД',
        line=dict(color='green', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Зависимость КПД от мощности',
        xaxis_title='Электрическая мощность (МВт)',
        yaxis_title='КПД (%)',
        template='plotly_white',
        width=600,
        height=400
    )
    
    return fig


def create_schematic_diagram():
    """
    Создание упрощенной тепловой схемы
    
    Возвращает:
    plotly.graph_objects.Figure: Фигура со схемой
    """
    fig = go.Figure()
    
    # Добавляем основные элементы схемы (упрощенно)
    # Котел
    fig.add_shape(type="rect",
        x0=0, y0=80, x1=40, y1=100,
        line=dict(color="orange", width=2),
        fillcolor="rgba(255, 165, 0, 0.1)"
    )
    fig.add_annotation(x=20, y=90, text="Котел", showarrow=False)
    
    # Турбина
    fig.add_shape(type="rect",
        x0=50, y0=40, x1=150, y1=100,
        line=dict(color="blue", width=2),
        fillcolor="rgba(0, 0, 255, 0.1)"
    )
    fig.add_annotation(x=100, y=70, text="Турбина", showarrow=False)
    
    # Конденсатор
    fig.add_shape(type="rect",
        x0=160, y0=20, x1=200, y1=60,
        line=dict(color="purple", width=2),
        fillcolor="rgba(128, 0, 128, 0.1)"
    )
    fig.add_annotation(x=180, y=40, text="Конденсатор", showarrow=False)
    
    # Насос
    fig.add_shape(type="circle",
        x0=80, y0=0, x1=120, y1=20,
        line=dict(color="green", width=2),
        fillcolor="rgba(0, 128, 0, 0.1)"
    )
    fig.add_annotation(x=100, y=10, text="Насос", showarrow=False)
    
    # Линии связи
    fig.add_shape(type="line",
        x0=40, y0=90, x1=50, y1=90,
        line=dict(color="red", width=2)
    )
    fig.add_shape(type="line",
        x0=150, y0=70, x1=160, y1=40,
        line=dict(color="red", width=2)
    )
    fig.add_shape(type="line",
        x0=180, y0=20, x1=100, y1=0,
        line=dict(color="blue", width=2)
    )
    fig.add_shape(type="line",
        x0=100, y0=20, x1=100, y1=40,
        line=dict(color="blue", width=2, dash="dash")
    )
    
    fig.update_layout(
        title='Упрощенная тепловая схема Т-100/120-130-3',
        xaxis=dict(visible=False, range=[0, 220]),
        yaxis=dict(visible=False, range=[0, 110]),
        template='plotly_white',
        width=700,
        height=500
    )
    
    return fig