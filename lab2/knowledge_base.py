from __future__ import annotations

"""
Модуль, отвечающий за загрузку продукционных правил из YAML-файла.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

import yaml


@dataclass(frozen=True)
class Rule:
    """Описывает одно продукционное правило."""

    id: str
    conditions: Sequence[str]
    conclusion: str


class KnowledgeBase:
    """База знаний, содержащая упорядоченный набор правил."""

    def __init__(self, rules: Sequence[Rule]) -> None:
        if not rules:
            raise ValueError("База знаний не может быть пустой.")
        self._rules: List[Rule] = list(rules)

    @property
    def rules(self) -> Sequence[Rule]:
        """Возвращает правила в исходном порядке."""
        return tuple(self._rules)

    @classmethod
    def from_yaml(cls, path: Path) -> "KnowledgeBase":
        """Загружает правила из YAML-файла."""
        if not path.exists():
            raise FileNotFoundError(f"Файл с правилами не найден: {path}")

        with path.open("r", encoding="utf-8") as file:
            payload = yaml.safe_load(file)

        raw_rules = payload.get("rules")
        if not isinstance(raw_rules, list):
            raise ValueError("Некорректный формат файла правил: отсутствует список 'rules'.")

        rules: List[Rule] = []
        for item in raw_rules:
            try:
                rule = Rule(
                    id=str(item["id"]),
                    conditions=tuple(item["conditions"]),
                    conclusion=str(item["conclusion"]),
                )
            except (KeyError, TypeError) as error:
                raise ValueError(f"Ошибка парсинга правила: {item}") from error
            rules.append(rule)

        return cls(rules)

