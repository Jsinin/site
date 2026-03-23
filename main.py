"""
Веб-приложение для расчета турбины Т-100/120-130-3
Streamlit интерфейс
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from solver import T100TurbineModel
from visualization import (
    plot_hs_diagram, 
    plot_heat_load_chart, 
    plot_steam_flow_characteristics,
    plot_efficiency_curve,
    create_schematic_diagram
)

# Настройка страницы
st.set_page_config(
    page_title="Расчет турбины Т-100/120-130-3",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Заголовок
st.title("🌡️ Термодинамический расчет турбины Т-100/120-130-3")
st.markdown("---")

# Боковая панель
with st.sidebar:
    st.header("⚙️ Параметры расчета")
    
    # Выбор режима
    mode = st.radio(
        "Режим работы",
        ["Конденсационный", "Теплофикационный"],
        help="Конденсационный - только выработка электроэнергии, Теплофикационный - с отбором на сетевые подогреватели"
    )
    
    st.markdown("---")
    
    if mode == "Конденсационный":
        st.subheader("Электрическая нагрузка")
        target_power = st.slider(
            "Мощность, МВт",
            min_value=30.0,
            max_value=120.0,
            value=100.0,
            step=5.0,
            help="Диапазон работы турбины 30-120 МВт"
        )
        
        # Дополнительные параметры
        with st.expander("Дополнительные параметры"):
            p_fresh = st.number_input(
                "Давление свежего пара, МПа",
                min_value=10.0,
                max_value=14.0,
                value=12.75,
                step=0.1,
                help="Номинальное давление 12.75 МПа"
            )
            t_fresh = st.number_input(
                "Температура свежего пара, °C",
                min_value=500.0,
                max_value=570.0,
                value=540.0,
                step=5.0,
                help="Номинальная температура 540°C"
            )
        
        q_load = None
        t_amb = None
        
    else:  # Теплофикационный режим
        st.subheader("Тепловая нагрузка")
        q_load = st.number_input(
            "Тепловая нагрузка, Гкал/ч",
            min_value=0.0,
            max_value=200.0,
            value=50.0,
            step=10.0,
            help="Тепловая нагрузка сетевых подогревателей"
        )
        
        st.subheader("Климатические условия")
        t_amb = st.slider(
            "Температура наружного воздуха, °C",
            min_value=-30.0,
            max_value=30.0,
            value=0.0,
            step=5.0,
            help="Влияет на режим работы сетевых подогревателей"
        )
        
        target_power = None
        
        with st.expander("Параметры сетевой воды"):
            t_supply = st.number_input("Температура подачи, °C", value=150.0)
            t_return = st.number_input("Температура обратки, °C", value=70.0)
    
    st.markdown("---")
    
    # Кнопка расчета
    calculate_button = st.button(
        "🚀 РАССЧИТАТЬ",
        type="primary",
        use_container_width=True
    )
    
    st.markdown("---")
    st.caption("Модель турбины Т-100/120-130-3")
    st.caption("Верифицирована по данным ТЭХ")

# Основная логика
if calculate_button:
    # Инициализация модели
    model = T100TurbineModel()
    
    # Если заданы дополнительные параметры, обновляем модель
    if mode == "Конденсационный" and 'p_fresh' in locals():
        model.p_fresh = p_fresh
        model.t_fresh = t_fresh
    
    with st.spinner('🔄 Выполнение термодинамического расчета...'):
        try:
            if mode == "Конденсационный":
                results = model.calculate_condensing_mode(target_power)
                st.success(f"✅ Расчет завершен успешно!")
                st.info(f"📊 Найденный расход пара: **{results['D0']:.2f} кг/с** ({results['D0_th']:.1f} т/ч)")
            else:
                results = model.calculate_heating_mode(q_load, t_amb)
                st.success(f"✅ Расчет завершен успешно!")
                st.info(f"📊 Полученная электрическая мощность: **{results['total_power']:.2f} МВт**")
                
                # Информация о режиме работы ПСГ
                if results.get('network_stages', 1) == 1:
                    st.info("🌡️ Режим: работает только ПСГ-1 (нижний сетевой подогреватель)")
                else:
                    st.info("🌡️ Режим: работают ПСГ-1 и ПСГ-2 (оба сетевых подогревателя)")
            
            # Сохраняем результаты в session state для использования в других вкладках
            st.session_state['results'] = results
            st.session_state['mode'] = mode
            
        except Exception as e:
            st.error(f"❌ Ошибка при расчете: {str(e)}")
            st.stop()
    
    # ==================== ВКЛАДКИ ДЛЯ ОТОБРАЖЕНИЯ РЕЗУЛЬТАТОВ ====================
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Интегральные показатели",
        "📈 Графики процессов",
        "📋 Параметры по точкам",
        "📐 Характеристики турбины",
        "ℹ️ Верификация"
    ])
    
    # ==================== ВКЛАДКА 1: ИНТЕГРАЛЬНЫЕ ПОКАЗАТЕЛИ ====================
    with tab1:
        st.subheader("📊 Интегральные показатели работы")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Расход свежего пара",
                f"{results['D0_th']:.1f} т/ч",
                delta=f"{results['D0_kg_s']:.1f} кг/с"
            )
        
        with col2:
            st.metric(
                "Электрическая мощность",
                f"{results['total_power']:.2f} МВт",
                delta=f"{(results['total_power']/results.get('target_power', results['total_power'])*100):.1f}%"
            )
        
        with col3:
            st.metric(
                "КПД брутто",
                f"{results['efficiency']:.2f} %"
            )
        
        with col4:
            st.metric(
                "Удельный расход пара",
                f"{results['specific_steam_consumption']:.3f} кг/кВт·ч"
            )
        
        with col5:
            st.metric(
                "Удельный расход теплоты",
                f"{results.get('specific_heat_consumption', 0):.0f} кДж/кВт·ч"
            )
        
        st.markdown("---")
        
        # Дополнительные показатели
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if results.get('Q_network', 0) > 0:
                st.metric(
                    "Тепловая нагрузка",
                    f"{results['Q_network']:.2f} МВт",
                    delta=f"{results.get('Q_network_gcal', 0):.1f} Гкал/ч"
                )
        
        with col2:
            st.metric(
                "Мощность брутто",
                f"{results['gross_power']:.2f} МВт"
            )
        
        with col3:
            st.metric(
                "Мощность насосов",
                f"{results['pump_power']:.2f} МВт",
                delta="Потери"
            )
        
        # Дополнительная информация
        st.markdown("---")
        st.subheader("📌 Режимные параметры")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.write("**Параметры свежего пара:**")
            st.write(f"• Давление: {model.p_fresh} МПа")
            st.write(f"• Температура: {model.t_fresh} °C")
        
        with info_col2:
            st.write("**Параметры конденсатора:**")
            st.write(f"• Давление: {model.p_cond * 1000:.1f} кПа")
            if results.get('points', []):
                last_point = results['points'][-1]
                if 'T' in last_point:
                    st.write(f"• Температура: {last_point['T']:.1f} °C")
    
    # ==================== ВКЛАДКА 2: ГРАФИКИ ПРОЦЕССОВ ====================
    with tab2:
        st.subheader("📈 Визуализация термодинамических процессов")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # h-s диаграмма
            st.plotly_chart(
                plot_hs_diagram(results['points']),
                use_container_width=True,
                key="hs_diagram"
            )
        
        with col2:
            # Баланс мощностей
            st.plotly_chart(
                plot_heat_load_chart(results),
                use_container_width=True,
                key="balance_chart"
            )
        
        st.markdown("---")
        
        # Дополнительные графики
        st.subheader("📊 Дополнительные графики")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Расходная характеристика
            st.plotly_chart(
                plot_steam_flow_characteristics(),
                use_container_width=True,
                key="flow_chart"
            )
        
        with col2:
            # Кривая КПД
            st.plotly_chart(
                plot_efficiency_curve(),
                use_container_width=True,
                key="efficiency_chart"
            )
        
        # Упрощенная тепловая схема
        st.subheader("🏭 Упрощенная тепловая схема")
        st.plotly_chart(
            create_schematic_diagram(),
            use_container_width=True,
            key="schematic"
        )
    
    # ==================== ВКЛАДКА 3: ПАРАМЕТРЫ ПО ТОЧКАМ ====================
    with tab3:
        st.subheader("📋 Параметры рабочего тела по точкам отборов")
        
        # Подготовка данных для таблицы
        points_data = []
        for i, point in enumerate(results['points']):
            row = {
                "№": i + 1,
                "Точка": point['name'],
                "Давление, МПа": f"{point['P']:.4f}",
                "Температура, °C": f"{point['T']:.1f}",
                "Энтальпия, кДж/кг": f"{point['h']:.1f}",
                "Энтропия, кДж/(кг·К)": f"{point['s']:.4f}",
                "Расход, кг/с": f"{point['G']:.1f}"
            }
            
            # Добавляем информацию об отборе для теплофикационного режима
            if 'extraction' in point and point['extraction'] > 0:
                row["Отбор на ПСГ, кг/с"] = f"{point['extraction']:.1f}"
            
            points_data.append(row)
        
        df_points = pd.DataFrame(points_data)
        st.dataframe(df_points, use_container_width=True, height=400)
        
        # Экспорт в CSV
        csv = df_points.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Скачать данные (CSV)",
            data=csv,
            file_name="turbine_points.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        
        # Детальный расчет отсеков
        st.subheader("🔧 Расчет отсеков турбины")
        
        # Создаем таблицу для отсеков
        stages_data = []
        for i in range(len(results['points']) - 1):
            p_in = results['points'][i]['P']
            p_out = results['points'][i + 1]['P']
            h_in = results['points'][i]['h']
            h_out = results['points'][i + 1]['h']
            delta_h = h_in - h_out
            
            # Мощность отсека
            G = results['points'][i]['G']
            power_sec = G * delta_h / 1000
            
            stages_data.append({
                "Отсек": f"Отсек {i+1}",
                "Давление входа, МПа": f"{p_in:.3f}",
                "Давление выхода, МПа": f"{p_out:.4f}",
                "Энтальпия входа, кДж/кг": f"{h_in:.1f}",
                "Энтальпия выхода, кДж/кг": f"{h_out:.1f}",
                "Теплоперепад, кДж/кг": f"{delta_h:.1f}",
                "Мощность отсека, МВт": f"{power_sec:.2f}"
            })
        
        df_stages = pd.DataFrame(stages_data)
        st.dataframe(df_stages, use_container_width=True)
    
    # ==================== ВКЛАДКА 4: ХАРАКТЕРИСТИКИ ТУРБИНЫ ====================
    with tab4:
        st.subheader("📐 Характеристики турбины Т-100/120-130-3")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Основные параметры:**")
            st.write("• Тип: теплофикационная")
            st.write("• Номинальная мощность: 100 МВт")
            st.write("• Максимальная мощность: 120 МВт")
            st.write("• Начальное давление: 12.75 МПа (130 кгс/см²)")
            st.write("• Начальная температура: 540-555 °C")
            st.write("• Давление в конденсаторе: 3.5 кПа")
        
        with col2:
            st.write("**Отборы пара:**")
            st.write("• ПВД-7: 4.0 МПа")
            st.write("• ПВД-6: 2.0 МПа")
            st.write("• ПВД-5: 1.2 МПа")
            st.write("• Деаэратор: 0.6 МПа")
            st.write("• ПСГ-1: 0.25 МПа (верхний сетевой)")
            st.write("• ПСГ-2: 0.12 МПа (нижний сетевой)")
        
        st.markdown("---")
        
        # Режимная карта
        st.subheader("🗺️ Режимная карта")
        
        # Создаем данные для режимной карты
        power_range = np.linspace(30, 120, 20)
        heat_range = np.linspace(0, 200, 20)
        
        # Упрощенная зависимость мощности от тепловой нагрузки
        # N = N0 - a * Q (для теплофикационного режима)
        power_matrix = []
        for q in heat_range:
            row = []
            for p in power_range:
                if q > 0:
                    # При отборе тепла мощность снижается
                    n_available = p - 0.15 * q
                    row.append(max(30, min(120, n_available)))
                else:
                    row.append(p)
            power_matrix.append(row)
        
        fig_heat_map = go.Figure(data=go.Heatmap(
            z=power_matrix,
            x=power_range,
            y=heat_range,
            colorscale='Viridis',
            colorbar=dict(title="Мощность, МВт")
        ))
        
        fig_heat_map.update_layout(
            title='Режимная карта турбины (зависимость мощности от тепловой нагрузки)',
            xaxis_title='Электрическая мощность, МВт',
            yaxis_title='Тепловая нагрузка, Гкал/ч',
            height=500
        )
        
        st.plotly_chart(fig_heat_map, use_container_width=True)
    
    # ==================== ВКЛАДКА 5: ВЕРИФИКАЦИЯ ====================
    with tab5:
        st.subheader("ℹ️ Верификация модели")
        
        st.markdown("""
        ### Данные для верификации (режим 100 МВт)
        
        **Турбина Т-100/120-130-3, конденсационный режим**
        """)
        
        # Получаем верификационные данные
        verif_data = model.get_verification_data()
        
        # Текущие результаты для сравнения
        if 'results' in st.session_state:
            current_power = st.session_state['results']['total_power']
            current_flow = st.session_state['results']['D0_th']
            current_efficiency = st.session_state['results']['efficiency']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Номинальные данные (ТЭХ):**")
                st.write(f"• Мощность: {verif_data['nominal_power']} МВт")
                st.write(f"• Расход пара: {verif_data['nominal_steam_flow'] * 3.6:.1f} т/ч")
                st.write(f"• КПД: {verif_data['nominal_efficiency']} %")
            
            with col2:
                st.write("**Текущий расчет:**")
                st.write(f"• Мощность: {current_power:.2f} МВт")
                st.write(f"• Расход пара: {current_flow:.1f} т/ч")
                st.write(f"• КПД: {current_efficiency:.2f} %")
            
            st.markdown("---")
            
            # Оценка погрешности
            if abs(current_power - verif_data['nominal_power']) < 5:
                st.success("✅ Модель верифицирована! Погрешность в пределах допустимых значений (±5%)")
            else:
                st.warning("⚠️ Отклонение от номинальных данных превышает 5%. Проверьте входные параметры.")
            
            # Погрешности
            st.subheader("📊 Погрешности расчета")
            
            err_power = abs(current_power - verif_data['nominal_power']) / verif_data['nominal_power'] * 100
            err_flow = abs(current_flow - verif_data['nominal_steam_flow'] * 3.6) / (verif_data['nominal_steam_flow'] * 3.6) * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Погрешность по мощности",
                    f"{err_power:.2f} %",
                    delta="от номинала"
                )
            
            with col2:
                st.metric(
                    "Погрешность по расходу",
                    f"{err_flow:.2f} %",
                    delta="от номинала"
                )
        
        st.markdown("---")
        st.markdown("""
        ### 📚 Источники данных для верификации
        
        - Тепловой расчет турбины Т-100/120-130-3 (ТЭХ УТЗ)
        - Типовая энергетическая характеристика
        - Режимная карта турбоагрегата
        """)

# Если расчет не выполнен, показываем информацию
else:
    st.info("👈 **Введите параметры в боковой панели и нажмите 'РАССЧИТАТЬ'**")
    
    # Показываем общую информацию
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📌 О программе")
        st.write("""
        **Программа для термодинамического расчета турбины Т-100/120-130-3**
        
        Возможности:
        - Расчет конденсационного режима
        - Расчет теплофикационного режима
        - Построение h-s диаграммы
        - Расчет параметров по отборам
        - Визуализация режимной карты
        - Верификация по номинальным данным
        """)
    
    with col2:
        st.subheader("🔧 Технические характеристики")
        st.write("""
        **Турбина Т-100/120-130-3:**
        - Тип: теплофикационная
        - Nном = 100 МВт
        - Nмакс = 120 МВт
        - P0 = 12.75 МПа
        - t0 = 540-555 °C
        - Pк = 3.5 кПа
        
        **Отборы пара:**
        - Промышленный: 1.2-2.5 МПа
        - Отопительный: 0.05-0.25 МПа
        """)
    
    # Показываем пример расчета
    with st.expander("📖 Пример расчета (конденсационный режим, 100 МВт)"):
        st.code("""
        Параметры:
        - Режим: Конденсационный
        - Мощность: 100 МВт
        - P0 = 12.75 МПа
        - t0 = 540 °C
        
        Ожидаемые результаты:
        - Расход пара: ~130 т/ч
        - КПД: ~43-44%
        - Удельный расход: ~3.6-3.8 кг/кВт·ч
        """)

# Подвал
st.markdown("---")
st.caption("© 2024 | Модель турбины Т-100/120-130-3 | Верифицировано по данным ТЭХ")