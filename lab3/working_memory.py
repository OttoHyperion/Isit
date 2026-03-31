"""
Модуль, реализующий рабочую память экспертной системы
"""
from typing import Dict, Any, List
from frame import Frame

class WorkingMemory:
    """Рабочая память для хранения текущих фактов и истории вывода"""
    
    def __init__(self):
        self.user_preferences: Dict[str, Any] = {}
        self.proto_frames: List[Frame] = []  # Протофреймы пользователя
        self.exo_frames: List[Frame] = []    # Экзофреймы из БЗ
        self.trace: list = []  # история вывода
    
    def set_preferences(self, preferences: Dict[str, Any]):
        """Устанавливает предпочтения пользователя"""
        self.user_preferences = preferences
    
    def add_proto_frame(self, proto_frame: Frame):
        """Добавляет протофрейм"""
        self.proto_frames.append(proto_frame)
    
    def add_exo_frame(self, exo_frame: Frame):
        """Добавляет экзофрейм"""
        self.exo_frames.append(exo_frame)
    
    def add_trace_entry(self, entry: Dict[str, Any]):
        """Добавляет запись в историю вывода"""
        self.trace.append(entry)
    
    def get_preferences(self) -> Dict[str, Any]:
        """Возвращает предпочтения пользователя"""
        return self.user_preferences
    
    def get_proto_frames(self) -> List[Frame]:
        """Возвращает протофреймы"""
        return self.proto_frames
    
    def get_exo_frames(self) -> List[Frame]:
        """Возвращает экзофреймы"""
        return self.exo_frames
    
    def get_trace(self) -> list:
        """Возвращает историю вывода"""
        return self.trace
    
    def clear(self):
        """Очищает рабочую память"""
        self.user_preferences = {}
        self.proto_frames = []
        self.exo_frames = []
        self.trace = []