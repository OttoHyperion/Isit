"""
Основной модуль запуска фреймовой экспертной системы
"""
from knowledge_base import KnowledgeBase
from inference_engine import InferenceEngine
from explanation_component import ExplanationComponent

def get_user_input():
    """Запрашивает у пользователя начальные факты"""
    print("Введите информацию о ваших предпочтениях для выбора места отдыха:")
    
    budget = int(input("Ваш бюджет (в рублях): "))
    
    health_restrictions = input("Есть ли у вас ограничения по здоровью? (да/нет): ").strip().lower()
    while health_restrictions not in ['да', 'нет']:
        health_restrictions = input("Пожалуйста, введите 'да' или 'нет': ").strip().lower()
    
    want_sea = input("Хотите ли вы отдых у моря? (да/нет): ").strip().lower()
    while want_sea not in ['да', 'нет']:
        want_sea = input("Пожалуйста, введите 'да' или 'нет': ").strip().lower()
    
    season = input("Какой сезон вы предпочитаете для отдыха? (лето/зима): ").strip().lower()
    while season not in ['лето', 'зима']:
        season = input("Пожалуйста, введите 'лето' или 'зима': ").strip().lower()
    
    want_mountains = input("Хотите ли вы отдых в горах? (да/нет): ").strip().lower()
    while want_mountains not in ['да', 'нет']:
        want_mountains = input("Пожалуйста, введите 'да' или 'нет': ").strip().lower()
    
    want_excursions = input("Хотите ли вы участвовать в экскурсиях? (да/нет): ").strip().lower()
    while want_excursions not in ['да', 'нет']:
        want_excursions = input("Пожалуйста, введите 'да' или 'нет': ").strip().lower()
    
    has_transport = input("У вас есть транспорт? (да/нет): ").strip().lower()
    while has_transport not in ['да', 'нет']:
        has_transport = input("Пожалуйста, введите 'да' или 'нет': ").strip().lower()
    
    short_vacation = input("Планируете ли вы короткий отпуск? (да/нет): ").strip().lower()
    while short_vacation not in ['да', 'нет']:
        short_vacation = input("Пожалуйста, введите 'да' или 'нет': ").strip().lower()
    
    return {
        "Бюджет": budget,
        "Ограничения по здоровью": health_restrictions,
        "Хочу море": want_sea,
        "Сезон": season,
        "Хочу горы": want_mountains,
        "Хочу экскурсии": want_excursions,
        "Есть транспорт": has_transport,
        "Короткий отпуск": short_vacation
    }

def main():
    """Демонстрация работы фреймовой экспертной системы"""
    print("Фреймовая экспертная система: Выбор места для отдыха")
    print("=" * 70)
    
    try:
        # Создаем компоненты системы
        kb = KnowledgeBase("knowledge_base.yaml")
        ie = InferenceEngine(kb)
        ec = ExplanationComponent(ie)
        
        print(f"Загружено {len(kb.get_all_frames())} фреймов из knowledge_base.yaml")
        
    except FileNotFoundError:
        print("Ошибка: Файл knowledge_base.yaml не найден!")
        print("Убедитесь, что файл находится в той же директории, что и main.py")
        return
    except Exception as e:
        print(f"Ошибка при загрузке базы знаний: {e}")
        return
    
    # Запрашиваем начальные факты у пользователя
    initial_facts = get_user_input()
    
    print("\nВведенные вами данные:")
    for fact, value in initial_facts.items():
        print(f"  {fact}: {value}")
    
    # Устанавливаем предпочтения и выполняем вывод
    ie.set_user_preferences(initial_facts)
    proto_frames = ie.frame_based_inference()

    
    # Выводим результаты
    if proto_frames:
        best_recommendation = ie.get_best_recommendation()
        print(f"\nЛучшая рекомендация: {best_recommendation}")
        
        print(f"\nПодробное объяснение для '{best_recommendation}':")
        detailed_explanation = ec.explain_recommendation(best_recommendation)
        print(detailed_explanation)
    else:
        print("\nНе удалось найти подходящие места отдыха на основе ваших предпочтений.")

if __name__ == "__main__":
    main()