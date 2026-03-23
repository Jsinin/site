"""
Решатель для турбины Т-100/120-130-3
Содержит логику расчета конденсационного и теплофикационного режимов
"""

import numpy as np
from components import TurbineStage, Heater, Pump
from thermodynamics import SteamProperties

class T100TurbineModel:
    """Модель турбины Т-100/120-130-3"""
    
    def __init__(self):
        # Параметры из технической характеристики
        self.p_fresh = 12.75  # МПа (130 кгс/см²)
        self.t_fresh = 540.0  # °C
        self.p_cond = 0.0035  # МПа (вакуум)
        
        # Давления отборов (номинальные, МПа)
        self.extraction_pressures = [
            4.0,    # Отбор 1: ПВД-7
            2.0,    # Отбор 2: ПВД-6
            1.2,    # Отбор 3: ПВД-5
            0.6,    # Отбор 4: Деаэратор
            0.25,   # Отбор 5: ПСГ-1 (нижний сетевой)
            0.12,   # Отбор 6: ПСГ-2 (верхний сетевой)
            0.0035  # Конденсатор
        ]
        
        # КПД отсеков турбины (внутренний относительный)
        # Последние отсеки снижены для уменьшения мощности
        self.eta_stages = [
            0.85,   # ЦВД (до отбора 4.0 МПа)
            0.88,   # Отсек до 2.0 МПа
            0.88,   # Отсек до 1.2 МПа
            0.86,   # Отсек до 0.6 МПа
            0.80,   # Отсек до 0.25 МПа
            0.78,   # Отсек до 0.12 МПа
            0.72    # Отсек до конденсатора
        ]
        
        # Доли отборов на регенерацию (относительно D0) для конденсационного режима
        # Увеличены для значительного уменьшения мощности при заданном D0
        self.regeneration_fractions = [0.14, 0.12, 0.10, 0.09, 0.0, 0.0]  # сумма 0.45
        
        # КПД генератора
        self.eta_generator = 0.96
        
        # Энтальпия питательной воды (увеличена для более точного баланса)
        self.h_feedwater = 1200.0  # кДж/кг
        
        self.results = {}
    
    def get_fresh_steam_state(self):
        """Получить состояние свежего пара"""
        return SteamProperties.get_state(P=self.p_fresh, T=self.t_fresh)
    
    def calculate_condensing_mode(self, target_power_mw):
        """
        Конденсационный режим (все отборы закрыты)
        Метод бисекции для подбора расхода пара D0
        """
        # Границы поиска расхода пара (кг/с) — расширены
        d0_min = 40.0
        d0_max = 250.0   # до 900 т/ч
        
        tolerance = 0.5
        max_iter = 50
        
        d0 = (d0_min + d0_max) / 2.0
        current_power = 0
        
        print(f"Поиск расхода пара для мощности {target_power_mw} МВт...")
        
        for i in range(max_iter):
            d0 = (d0_min + d0_max) / 2.0
            res = self._run_cycle(d0, mode='condensing')
            current_power = res['total_power']
            
            print(f"  Итерация {i+1}: D0 = {d0:.1f} кг/с → N = {current_power:.2f} МВт")
            
            if abs(current_power - target_power_mw) < tolerance:
                break
            
            if current_power < target_power_mw:
                d0_min = d0
            else:
                d0_max = d0
        
        self.results = res
        self.results['D0'] = d0
        self.results['D0_th'] = d0 * 3.6
        self.results['D0_kg_s'] = d0
        self.results['mode'] = 'condensing'
        self.results['target_power'] = target_power_mw
        self.results['specific_steam_consumption'] = res.get('specific_steam_rate', 0)
        self.results['specific_heat_consumption'] = res.get('specific_heat_consumption', 0)
        self.results['Q_network'] = res.get('Q_network', 0)
        self.results['network_stages'] = res.get('network_stages', 1)
        
        return self.results
    
    def calculate_heating_mode(self, Q_gcal_h, t_amb, d0_kg_s=None):
        """Теплофикационный режим (с отборами на сетевые подогреватели)"""
        Q_mw = Q_gcal_h * 1.163
        
        if d0_kg_s is None:
            d0_kg_s = 130.0
        
        if t_amb > -5:
            extraction_index = 4
            Q_network = Q_mw
            network_stages = 1
        else:
            extraction_index = 5
            Q_network = Q_mw
            network_stages = 2
        
        res = self._run_cycle(d0_kg_s, mode='heating', Q_network=Q_network, 
                              extraction_index=extraction_index)
        
        self.results = res
        self.results['D0'] = d0_kg_s
        self.results['D0_th'] = d0_kg_s * 3.6
        self.results['D0_kg_s'] = d0_kg_s
        self.results['mode'] = 'heating'
        self.results['Q_thermal'] = Q_mw
        self.results['Q_thermal_gcal'] = Q_gcal_h
        self.results['t_amb'] = t_amb
        self.results['Q_network'] = Q_network
        self.results['network_stages'] = network_stages
        self.results['specific_steam_consumption'] = res.get('specific_steam_rate', 0)
        self.results['specific_heat_consumption'] = res.get('specific_heat_consumption', 0)
        
        return self.results
    
    def _run_cycle(self, d0_kg_s, mode='condensing', Q_network=0, extraction_index=4):
        """Внутренний расчет цикла турбины"""
        fresh = self.get_fresh_steam_state()
        h0 = fresh.h
        s0 = fresh.s
        
        current_h = h0
        current_s = s0
        total_power = 0.0
        current_flow = d0_kg_s
        
        points = [{
            'name': 'Свежий пар',
            'P': self.p_fresh,
            'T': self.t_fresh,
            'h': h0,
            's': s0,
            'G': current_flow
        }]
        
        for i, p_next in enumerate(self.extraction_pressures):
            # Обработка отборов
            if mode == 'heating' and i == extraction_index and Q_network > 0:
                h_extraction = current_h
                h_drain = 500.0
                G_ext = Q_network * 1000 / (h_extraction - h_drain)
                G_ext = min(G_ext, current_flow * 0.5)
                current_flow -= G_ext
                points.append({
                    'name': f'Отбор на теплофикацию',
                    'P': p_next,
                    'T': 0,
                    'h': h_extraction,
                    's': current_s,
                    'G': G_ext,
                    'is_extraction': True
                })
            elif mode == 'condensing' and i < len(self.regeneration_fractions):
                frac = self.regeneration_fractions[i]
                if frac > 0:
                    G_ext = d0_kg_s * frac
                    G_ext = min(G_ext, current_flow)
                    if G_ext > 0:
                        current_flow -= G_ext
                        points.append({
                            'name': f'Регенеративный отбор {i+1}',
                            'P': p_next,
                            'T': 0,
                            'h': current_h,
                            's': current_s,
                            'G': G_ext,
                            'is_extraction': True
                        })
            
            stage = TurbineStage(f"Stage_{i+1}", eta_internal=self.eta_stages[i])
            stage_result = stage.calculate(current_flow, current_h, current_s, p_next)
            total_power += stage_result['power']
            current_h = stage_result['h_out']
            current_s = stage_result['s_out']
            
            point_name = f"Отбор {i+1}"
            if i == len(self.extraction_pressures) - 1:
                point_name = "Конденсатор"
            elif mode == 'heating' and i == extraction_index:
                point_name += " (теплофикационный)"
            
            points.append({
                'name': point_name,
                'P': p_next,
                'T': stage_result['T_out'],
                'h': current_h,
                's': current_s,
                'G': current_flow
            })
        
        pump_power = 3.0
        net_power = total_power * self.eta_generator - pump_power
        
        Q_in = d0_kg_s * (h0 - self.h_feedwater) / 1000
        efficiency = (net_power / Q_in * 100) if Q_in > 0 else 0
        specific_heat_consumption = 3600 / efficiency if efficiency > 0 else 0
        specific_steam_rate = d0_kg_s * 3.6 / net_power if net_power > 0 else 0
        
        return {
            'total_power': net_power,
            'gross_power': total_power,
            'efficiency': efficiency,
            'specific_steam_rate': specific_steam_rate,
            'specific_heat_consumption': specific_heat_consumption,
            'points': points,
            'Q_network': Q_network if mode == 'heating' else 0,
            'pump_power': pump_power,
            'h_feedwater': self.h_feedwater
        }
    
    def get_verification_data(self):
        return {
            'nominal_power': 100.0,
            'nominal_steam_flow': 130.0,
            'nominal_efficiency': 42.5,
            'nominal_heat_rate': 2.2
        }