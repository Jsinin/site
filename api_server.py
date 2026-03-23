"""
Flask API сервер для расчета турбины Т-100/120-130-3
Запуск: python api_server.py
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solver import T100TurbineModel
import traceback

app = Flask(__name__)
CORS(app)  # Разрешить запросы с сайта (CORS)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    Основной endpoint для расчета
    Ожидает JSON: {turbineType, condPower, heatLoad, heatTemp}
    Возвращает: результаты расчета
    """
    try:
        data = request.json
        print(f"Получены данные: {data}")
        
        turbine_type = data.get('turbineType', 'cond')
        
        model = T100TurbineModel()
        
        if turbine_type == 'cond':
            # Конденсационный режим
            target_power = float(data.get('condPower', 100))
            print(f"Расчет конденсационного режима, мощность: {target_power} МВт")
            results = model.calculate_condensing_mode(target_power)
        else:
            # Теплофикационный режим
            heat_load = float(data.get('heatLoad', 50))
            temp_amb = float(data.get('heatTemp', 0))
            temp_supply = float(data.get('tempSupply', 150))  # Температура прямой воды
            temp_return = float(data.get('tempReturn', 70))    # Температура обратной воды
    
            print(f"Расчет теплофикационного режима:")
            print(f"  Тепловая нагрузка: {heat_load} Гкал/ч")
            print(f"  Температура воздуха: {temp_amb}°C")
            print(f"  Температура прямой воды: {temp_supply}°C")
            print(f"  Температура обратной воды: {temp_return}°C")
    
    results = model.calculate_heating_mode(heat_load, temp_amb)
        
        # Форматируем результаты для фронтенда
        response = {
            'success': True,
            'data': {
                'total_power': round(results.get('total_power', 0), 2),
                'efficiency': round(results.get('efficiency', 0), 2),
                'D0_th': round(results.get('D0_th', 0), 1),
                'D0_kg_s': round(results.get('D0_kg_s', 0), 2),
                'specific_steam_consumption': round(results.get('specific_steam_consumption', 0), 3),
                'Q_network': round(results.get('Q_network', 0), 2),
                'mode': results.get('mode', 'condensing'),
                'points': results.get('points', []),
                'gross_power': round(results.get('gross_power', 0), 2),
                'pump_power': round(results.get('pump_power', 0), 2)
            }
        }
        
        print(f"Расчет завершен успешно: {response['data']['total_power']} МВт")
        return jsonify(response)
        
    except Exception as e:
        error_msg = f"Ошибка при расчете: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg,
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Проверка работоспособности API"""
    return jsonify({
        'status': 'ok', 
        'message': 'API сервер турбины работает',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 ЗАПУСК API СЕРВЕРА ТУРБИНЫ Т-100/120-130-3")
    print("=" * 60)
    print("📍 Адрес: http://localhost:5000")
    print("🔗 Endpoint: POST /api/calculate")
    print("💚 Проверка: GET /api/health")
    print("=" * 60)
    print("️  НЕ ЗАКРЫВАЙТЕ ЭТО ОКНО ПОКА РАБОТАЕТ САЙТ!")
    print("=" * 60)
    app.run(debug=True, port=5000, host='0.0.0.0')