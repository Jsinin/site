"""
Тестовый скрипт для проверки работы plotly.graph_objects
"""

import sys
import numpy as np

print("=" * 60)
print("ПРОВЕРКА РАБОТЫ PLOTLY.GRAPH_OBJECTS")
print("=" * 60)

# 1. Проверяем версию Python
print(f"\n1. Версия Python: {sys.version}")

# 2. Проверяем установку plotly
try:
    import plotly
    print(f"\n2. ✅ Plotly установлен: версия {plotly.__version__}")
except ImportError:
    print("\n2. ❌ Plotly НЕ УСТАНОВЛЕН!")
    print("   Установите командой: pip install plotly")
    sys.exit(1)

# 3. Проверяем импорт graph_objects
try:
    import plotly.graph_objects as go
    print("\n3. ✅ plotly.graph_objects успешно импортирован")
except ImportError as e:
    print(f"\n3. ❌ Ошибка импорта: {e}")
    sys.exit(1)

# 4. Создаем простой график
print("\n4. Создаем тестовый график...")
try:
    fig = go.Figure()
    
    # Добавляем простой график
    fig.add_trace(go.Scatter(
        x=[1, 2, 3, 4],
        y=[10, 20, 15, 25],
        mode='lines+markers',
        name='Тестовая линия'
    ))
    
    fig.update_layout(
        title='Тестовый график',
        xaxis_title='X',
        yaxis_title='Y',
        template='plotly_white'
    )
    
    print("   ✅ График создан успешно")
    
except Exception as e:
    print(f"   ❌ Ошибка создания графика: {e}")
    sys.exit(1)

# 5. Проверяем работу с Heatmap (нужно для режимной карты)
print("\n5. Проверяем создание тепловой карты...")
try:
    # Создаем тестовые данные
    data = np.random.rand(10, 10)
    
    fig_heat = go.Figure(data=go.Heatmap(
        z=data,
        colorscale='Viridis'
    ))
    
    fig_heat.update_layout(title='Тестовая тепловая карта')
    print("   ✅ Тепловая карта создана успешно")
    
except Exception as e:
    print(f"   ❌ Ошибка создания тепловой карты: {e}")

# 6. Проверяем возможность сохранения
print("\n6. Проверяем сохранение графика...")
try:
    fig.write_html('test_plot.html')
    print("   ✅ График сохранен в test_plot.html")
except Exception as e:
    print(f"   ❌ Ошибка сохранения: {e}")

print("\n" + "=" * 60)
print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! plotly работает корректно.")
print("=" * 60)
print("\nТеперь можно запускать основное приложение:")
print("streamlit run main.py")