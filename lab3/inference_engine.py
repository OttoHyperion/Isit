"""
Модуль, реализующий механизм логического вывода для фреймовой системы
"""
from typing import Dict, Any, List, Optional
from knowledge_base import KnowledgeBase
from working_memory import WorkingMemory
from frame import Frame

class InferenceEngine:
    """Механизм логического вывода для фреймовой системы """
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.working_memory = WorkingMemory()
    
    def reset(self):
        """Сбрасывает рабочую память"""
        self.working_memory.clear()
    
    def set_user_preferences(self, preferences: Dict[str, Any]):
        """Устанавливает и обрабатывает предпочтения пользователя"""
        # Преобразуем числовые значения бюджета в категории
        budget = preferences.get("Бюджет", 0)
        if budget < 50000:
            budget_category = "низкий"
        elif budget < 100000:
            budget_category = "средний"
        else:
            budget_category = "высокий"
        
        # Определяем возможность поездки за границу
        health_restrictions = preferences.get("Ограничения по здоровью", "нет")
        can_go_abroad = "да" if health_restrictions == "нет" and budget_category in ["средний", "высокий"] else "нет"
        
        # Определяем доступность пляжного отдыха
        want_sea = preferences.get("Хочу море", "нет")
        season = preferences.get("Сезон", "лето")
        beach_available = "да" if want_sea == "да" and season == "лето" else "нет"
        
        # Определяем доступность горного отдыха
        want_mountains = preferences.get("Хочу горы", "нет")
        mountain_available = "да" if want_mountains == "да" else "нет"
        
        # Определяем доступность городских туров
        want_excursions = preferences.get("Хочу экскурсии", "нет")
        has_transport = preferences.get("Есть транспорт", "нет")
        city_tour_available = "да" if want_excursions == "да" and has_transport == "да" else "нет"
        
        processed_preferences = {
            "Бюджет": budget_category,
            "Возможна заграница": can_go_abroad,
            "Хочу море": want_sea,
            "Хочу горы": want_mountains,
            "Хочу экскурсии": want_excursions,
            "Сезон": season,
            "Короткий отпуск": preferences.get("Короткий отпуск", "нет"),
            "Есть транспорт": has_transport
        }
        
        self.working_memory.set_preferences(processed_preferences)
    
    def frame_based_inference(self) -> List[Frame]:
        """Выполняет вывод на основе фреймов согласно теории Минского"""
        preferences = self.working_memory.get_preferences()
        specific_locations = self.kb.get_specific_locations()
        
        # 1. Создаем протофреймы для каждого возможного места
        proto_frames = []
        matched_frames = []
        
        for location in specific_locations:
            # 2. Создаем протофрейм
            proto_frame = location.create_proto_frame()
            self.working_memory.add_proto_frame(proto_frame)
            
            # 3. Связываем с экзофреймом (уже сделано в create_proto_frame)
            self.working_memory.add_exo_frame(location)
            
            # 4. Заполняем слоты на основе предпочтений пользователя
            # Бюджет
            budget_pref = preferences.get("Бюджет")
            if budget_pref:
                try:
                    proto_frame.set_slot_value("бюджет_требование", budget_pref)
                except ValueError:
                    continue  # Пропускаем несовместимые варианты
            
            # Страна
            country_pref = "заграница" if preferences.get("Возможна заграница") == "да" else "Россия"
            proto_frame.set_slot_value("страна", country_pref)
            
            # Длительность
            duration_pref = "короткий" if preferences.get("Короткий отпуск") == "да" else "длинный"
            proto_frame.set_slot_value("длительность", duration_pref)
            
            # Сезон (для горного отдыха)
            if location.get_slot_value("требует_горы"):
                proto_frame.set_slot_value("сезон", preferences.get("Сезон", "лето"))
            
            # Проверяем совместимость через IF-NEEDED процедуру
            compatibility_slot = proto_frame.get_slot("совместимость")
            if compatibility_slot:
                compatibility = proto_frame.get_slot_value("совместимость")
            else:
                # Вычисляем совместимость вручную
                compatibility = self._calculate_manual_compatibility(proto_frame, preferences)
            
            if compatibility and compatibility > 0.3:
                matched_frames.append(proto_frame)
                self.working_memory.add_trace_entry({
                    "протофрейм": proto_frame.name,
                    "экзофрейм": location.name,
                    "совместимость": compatibility
                })
        
        return matched_frames
    
    def _calculate_manual_compatibility(self, proto_frame: Frame, preferences: Dict[str, Any]) -> float:
        """Ручной расчет совместимости для демонстрации"""
        score = 0.0
        total_checks = 0
        
        # Проверка бюджета
        budget_match = proto_frame.get_slot_value("бюджет_требование") == preferences.get("Бюджет")
        if budget_match:
            score += 1.0
        total_checks += 1
        
        # Проверка страны
        country_pref = "заграница" if preferences.get("Возможна заграница") == "да" else "Россия"
        country_match = proto_frame.get_slot_value("страна") == country_pref
        if country_match:
            score += 1.0
        total_checks += 1
        
        # Проверка длительности
        duration_pref = "короткий" if preferences.get("Короткий отпуск") == "да" else "длинный"
        duration_match = proto_frame.get_slot_value("длительность") == duration_pref
        if duration_match:
            score += 1.0
        total_checks += 1
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def get_best_recommendation(self) -> Optional[str]:
        """Возвращает лучшую рекомендацию"""
        proto_frames = self.working_memory.get_proto_frames()
        if proto_frames:
            # Берем первый (наиболее совместимый) протофрейм
            best_frame = proto_frames[0]
            # Получаем имя исходного экзофрейма
            ako_frame = best_frame.slots["AKO"].value
            if ako_frame:
                return ako_frame.name
        return None