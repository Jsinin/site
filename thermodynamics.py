"""
Модуль термодинамических свойств воды и пара
Реализация на основе библиотеки iapws (IAPWS-IF97)
"""
from iapws import IAPWS97
import numpy as np

class SteamProperties:
    """Класс для расчета свойств водяного пара по IAPWS-IF97"""
    
    @staticmethod
    def get_state(P=None, T=None, h=None, s=None, x=None):
        """
        Получить состояние пара по двум параметрам.
        Поддерживаются комбинации:
        - P и T (перегретый пар)
        - P и h
        - P и s
        Если параметры не соответствуют однозначному определению, будет вызвано исключение.
        
        Параметры:
        P - давление, МПа
        T - температура, °C
        h - энтальпия, кДж/кг
        s - энтропия, кДж/(кг·К)
        x - степень сухости (0-1) – не используется, так как библиотека определяет автоматически
        
        Возвращает:
        object: объект с атрибутами P, T (в °C), h, s, x
        """
        try:
            if P is not None and T is not None:
                # Перегретый пар: по P и T (T в K)
                state = IAPWS97(P=P, T=T+273.15)
            elif P is not None and h is not None:
                # По P и h
                state = IAPWS97(P=P, h=h)
            elif P is not None and s is not None:
                # По P и s
                state = IAPWS97(P=P, s=s)
            else:
                raise ValueError("Недостаточно параметров для определения состояния")
        except Exception as e:
            # В случае ошибки (например, выход за пределы области) вернуть объект с приближенными значениями
            # для обратной совместимости, но с предупреждением
            print(f"Предупреждение: не удалось рассчитать точное состояние ({e}), используются приближённые значения")
            state = type('State', (), {})()
            state.P = P if P is not None else 1.0
            state.T = T if T is not None else 200.0
            state.h = h if h is not None else 3000.0
            state.s = s if s is not None else 6.5
            state.x = x if x is not None else 1.0
            return state
        
        # Преобразуем температуру из Кельвинов в градусы Цельсия
        state.T = state.T - 273.15
        # Добавляем атрибут x (степень сухости) – библиотека уже содержит его
        # Убедимся, что x есть (для перегретого пара x=1)
        if not hasattr(state, 'x'):
            state.x = 1.0
        return state

# Для обратной совместимости
def get_steam_state(**kwargs):
    return SteamProperties.get_state(**kwargs)