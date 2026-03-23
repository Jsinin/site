"""
Модуль компонентов тепловой схемы
Турбина, подогреватели, насосы
"""

import numpy as np
from thermodynamics import SteamProperties

class Component:
    """Базовый класс для всех компонентов"""
    def __init__(self, name):
        self.name = name
        self.inlet = None
        self.outlet = None

class TurbineStage(Component):
    """Ступень турбины (отсек между отборами)"""
    
    def __init__(self, name, eta_internal=0.85):
        super().__init__(name)
        self.eta_internal = eta_internal  # Внутренний относительный КПД
        self.power = 0.0  # Мощность, МВт
    
    def calculate(self, mass_flow, h_in, s_in, p_out):
        """
        Расчет расширения в ступени
        
        Параметры:
        mass_flow (float): Расход пара, кг/с
        h_in (float): Энтальпия на входе, кДж/кг
        s_in (float): Энтропия на входе, кДж/(кг·К)
        p_out (float): Давление на выходе, МПа
        
        Возвращает:
        dict: Результаты расчета
        """
        # Изоэнтропное расширение
        state_ideal = SteamProperties.get_state(P=p_out, s=s_in)
        h_ideal = state_ideal.h
        
        # Реальное расширение (с учетом КПД)
        h_out = h_in - self.eta_internal * (h_in - h_ideal)
        
        # Мощность ступени: N = G * (h_in - h_out) / 1000 (кВт -> МВт)
        self.power = mass_flow * (h_in - h_out) / 1000.0
        
        # Свойства на выходе
        state_out = SteamProperties.get_state(P=p_out, h=h_out)
        
        return {
            'h_out': h_out,
            's_out': state_out.s,
            'T_out': state_out.T,  # уже в °C
            'x_out': state_out.x if hasattr(state_out, 'x') else 1.0,
            'power': self.power
        }

class Heater(Component):
    """Подогреватель (ПВД, ПНД, деаэратор)"""
    
    def __init__(self, name, type='low_pressure'):
        super().__init__(name)
        self.type = type  # low_pressure, deaerator, high_pressure, network
        self.duty = 0.0  # Тепловая нагрузка, МВт
        self.drain_mass_flow = 0.0  # Расход дренажа, кг/с
    
    def calculate_heat_balance(self, Q_required, h_steam_in, h_drain_out, h_water_in, h_water_out):
        """
        Упрощенный тепловой баланс подогревателя
        
        Параметры:
        Q_required (float): Требуемая тепловая нагрузка, МВт
        h_steam_in (float): Энтальпия греющего пара, кДж/кг
        h_drain_out (float): Энтальпия дренажа, кДж/кг
        h_water_in (float): Энтальпия воды на входе, кДж/кг
        h_water_out (float): Энтальпия воды на выходе, кДж/кг
        
        Возвращает:
        float: Расход греющего пара, кг/с
        """
        # Теплота, отдаваемая паром при конденсации
        heat_released = h_steam_in - h_drain_out
        
        if heat_released <= 0:
            return 0
        
        # Расход греющего пара: G_steam = Q / (h_steam - h_drain)
        self.drain_mass_flow = Q_required * 1000 / heat_released  # МВт -> кВт
        self.duty = Q_required
        
        return self.drain_mass_flow

class Pump(Component):
    """Насос"""
    
    def __init__(self, name, eta_pump=0.80):
        super().__init__(name)
        self.eta_pump = eta_pump  # КПД насоса
        self.power = 0.0  # Мощность привода, МВт
    
    def calculate(self, mass_flow, p_in, p_out, h_in, v_in):
        """
        Расчет насоса
        
        Параметры:
        mass_flow (float): Расход воды, кг/с
        p_in (float): Давление на входе, МПа
        p_out (float): Давление на выходе, МПа
        h_in (float): Энтальпия на входе, кДж/кг
        v_in (float): Удельный объем воды, м³/кг
        
        Возвращает:
        dict: Результаты расчета
        """
        # Изоэнтропная работа сжатия
        delta_p = p_out - p_in  # МПа
        work_ideal = delta_p * v_in * 1000  # кДж/кг (1 МПа·м³/кг = 1000 кДж/кг)
        
        # Реальная работа с учетом КПД
        work_real = work_ideal / self.eta_pump
        
        # Энтальпия на выходе
        h_out = h_in + work_real
        
        # Мощность привода
        self.power = mass_flow * work_real / 1000  # МВт
        
        return {
            'h_out': h_out,
            'work_real': work_real,
            'power': self.power
        }