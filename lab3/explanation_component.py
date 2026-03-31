"""
Модуль, реализующий компонент объяснения для фреймовой системы
"""
from typing import List, Dict, Any
from inference_engine import InferenceEngine

class ExplanationComponent:
    """Компонента объяснения для фреймовой системы """
    
    def __init__(self, inference_engine: InferenceEngine):
        self.ie = inference_engine
    
    def explain_recommendation(self, location_name: str) -> str:
        """Объясняет, почему данное место было рекомендовано"""
        # Находим соответствующий протофрейм
        proto_frames = self.ie.working_memory.get_proto_frames()
        target_proto = None
        
        for proto in proto_frames:
            ako_frame = proto.slots["AKO"].value
            if ako_frame and ako_frame.name == location_name:
                target_proto = proto
                break
        
        if not target_proto:
            return f"Место '{location_name}' не найдено среди рекомендаций"
        
        # Получаем объяснение через IF-NEEDED процедуру
        reason_slot = target_proto.get_slot("причина_рекомендации")
        if reason_slot:
            reason = target_proto.get_slot_value("причина_рекомендации")
        else:
            # Ручное объяснение
            reasons = []
            budget = target_proto.get_slot_value("бюджет_требование")
            if budget:
                reasons.append(f"Бюджет: {budget}")
            country = target_proto.get_slot_value("страна")
            if country:
                reasons.append(f"Страна: {country}")
            duration = target_proto.get_slot_value("длительность")
            if duration:
                reasons.append(f"Длительность: {duration}")
            season = target_proto.get_slot_value("сезон")
            if season:
                reasons.append(f"Сезон: {season}")
            reason = "; ".join(reasons) if reasons else "Общие характеристики совпадают"
        
        explanation = f"Место '{location_name}' рекомендовано по следующим причинам:\n"
        explanation += f"  - {reason}"
        
        return explanation

    
    def get_inference_trace(self) -> List[Dict[str, Any]]:
        """Возвращает историю вывода"""
        return self.ie.working_memory.get_trace()