"""
Модуль, реализующий базу знаний на основе фреймов
"""
import yaml
from typing import Dict, List, Any, Optional
from frame import Frame, Slot, DataType, InheritanceType, TriggerType

class KnowledgeBase:
    """База знаний, хранящая фреймы согласно теории """
    
    def __init__(self, yaml_file: str):
        self.frames: Dict[str, Frame] = {}
        self._procedures = {}
        self.load_from_yaml(yaml_file)
    
    def _register_procedures(self):
        """Регистрация встроенных процедур"""
        self._procedures["calculate_compatibility"] = self._calculate_compatibility
        self._procedures["get_recommendation_reason"] = self._get_recommendation_reason
        self._procedures["validate_budget"] = self._validate_budget
        self._procedures["compute_country"] = self._compute_country
    
    def _calculate_compatibility(self, frame) -> float:
        """IF-NEEDED процедура для расчета совместимости"""
        # Получаем предпочтения из рабочей памяти (для демонстрации)
        # В реальной системе это должно быть передано через контекст
        return 0.75  # Заглушка
    
    def _get_recommendation_reason(self, frame) -> str:
        """IF-NEEDED процедура для получения причины рекомендации"""
        reasons = []
        budget = frame.get_slot_value("бюджет_требование")
        if budget:
            reasons.append(f"Бюджет: {budget}")
        country = frame.get_slot_value("страна")
        if country:
            reasons.append(f"Страна: {country}")
        season = frame.get_slot_value("сезон")
        if season:
            reasons.append(f"Сезон: {season}")
        duration = frame.get_slot_value("длительность")
        if duration:
            reasons.append(f"Длительность: {duration}")
        return "; ".join(reasons) if reasons else "Общие характеристики"
    
    def _validate_budget(self, frame, old_value, new_value):
        """IF-ADDED процедура для валидации бюджета"""
        if new_value not in ["низкий", "средний", "высокий"]:
            raise ValueError(f"Недопустимое значение бюджета: {new_value}")
    
    def _compute_country(self, frame) -> str:
        """IF-NEEDED процедура для вычисления страны"""
        budget = frame.get_slot_value("бюджет_требование")
        if budget == "низкий":
            return "Россия"
        else:
            return "заграница"
    
    def _parse_triggers(self, trigger_data: Dict[str, Any]) -> Dict[TriggerType, callable]:
        triggers = {}
        for trigger_type_str, proc_name in trigger_data.items():
            # Убираем кавычки и приводим к правильному формату
            clean_trigger_str = trigger_type_str.strip('"\'')
            try:
                trigger_type = TriggerType(clean_trigger_str)
                if proc_name in self._procedures:
                    triggers[trigger_type] = self._procedures[proc_name]
            except ValueError:
                print(f"Предупреждение: неизвестный тип триггера '{clean_trigger_str}'")
                continue
        return triggers
    
    def load_from_yaml(self, yaml_file: str):
        """Загружает фреймы из YAML файла согласно теории Минского"""
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Регистрируем процедуры
        self._register_procedures()
        
        # Сначала создаём все фреймы
        frame_objects = {}
        for frame_data in data['frames']:
            name = frame_data['name']
            frame_objects[name] = Frame(name)
        
        # Устанавливаем слоты и AKO связи
        for frame_data in data['frames']:
            name = frame_data['name']
            frame = frame_objects[name]
            
            # Устанавливаем AKO (родительский фрейм)
            if 'ako' in frame_data and frame_data['ako']:
                parent_name = frame_data['ako']
                if parent_name in frame_objects:
                    frame.set_ako(frame_objects[parent_name])
            
            # Устанавливаем слоты
            if 'slots' in frame_data:
                for slot_data in frame_data['slots']:
                    slot_name = slot_data['name']
                    
                    # Определяем тип данных
                    data_type = DataType(slot_data.get('data_type', 'TEXT'))
                    
                    # Определяем тип наследования
                    inheritance = InheritanceType(slot_data.get('inheritance', 'O'))
                    
                    # Получаем значение
                    value = slot_data.get('value')
                    
                    # Получаем диапазон значений
                    range_values = slot_data.get('range', [])
                    
                    # Парсим триггеры
                    triggers = {}
                    if 'triggers' in slot_data:
                        triggers = self._parse_triggers(slot_data['triggers'])
                    
                    # Создаем слот
                    slot = Slot(
                        name=slot_name,
                        value=value,
                        data_type=data_type,
                        inheritance=inheritance,
                        range_values=range_values,
                        triggers=triggers
                    )
                    
                    frame.add_slot(slot)
        
        self.frames = frame_objects
    
    def get_frame(self, name: str) -> Optional[Frame]:
        """Возвращает фрейм по имени"""
        return self.frames.get(name)
    
    def get_all_frames(self) -> List[Frame]:
        """Возвращает все фреймы"""
        return list(self.frames.values())
    
    def get_specific_locations(self) -> List[Frame]:
        """Возвращает только конкретные места (не абстрактные типы)"""
        specific_names = [
            "Черноморье", "Крым", "Турция", "Таиланд", "Кавказ", "Сочи", "Домбай", 
            "Карпаты", "Альпы", "Москва", "Казань", "Париж", "Прага"
        ]
        return [self.frames[name] for name in specific_names if name in self.frames]